import Foundation
import WebKit

/// 启动内嵌 Node.js 运行时（nodejs-mobile 的 node_start），在独立线程中运行游戏服务端。
final class NodeRunner {

    /// 供界面诊断：存档目录绝对路径
    static var saveDirPath = ""
    /// 供界面诊断：node_start 返回码（nil = 尚未返回/仍在运行）
    static var nodeExitCode: Int32? = nil
    /// 供界面诊断：引擎启动时间戳
    static var startTime = Date()
    /// 供界面诊断：健康检查最近一次错误描述
    static var lastHealthError: String? = nil

    /// 阻塞调用 node_start 并常驻事件循环，必须在后台线程执行。
    /// - Parameters:
    ///   - gameDir: 打包进 App 的 game-data 目录绝对路径
    ///   - saveDir: 存档目录绝对路径（App Documents 下）
    static func start(gameDir: String, saveDir: String) {
        saveDirPath = saveDir
        startTime = Date()
        let script = gameDir + "/android-bootstrap.cjs"
        let arguments = ["node", script, gameDir, saveDir]

        // 重定向 Node 的 stdout/stderr 到存档目录日志文件：
        // iOS 上 Node 的 console 默认无处可去，启动失败原因会静默丢失，
        // 写文件后可通过存档目录/empress-node.log 直接定位。
        do {
            try FileManager.default.createDirectory(atPath: saveDir, withIntermediateDirectories: true)
            // iOS 进程默认 cwd 是只读根目录，若服务端存在相对路径写操作会直接崩溃；
            // 切到可写存档目录兜底（所有关键路径均为绝对路径，不受影响）。
            chdir(saveDir)
            let logPath = saveDir + "/empress-node.log"
            if let file = fopen(logPath, "w") {
                dup2(fileno(file), fileno(stdout))
                dup2(fileno(file), fileno(stderr))
                fflush(file)
            }
        } catch {
            NSLog("[Empress] cannot create saveDir: %@", error.localizedDescription)
        }

        DispatchQueue.global(qos: .userInitiated).async {
            let cArgs = arguments.map { strdup($0) }
            defer { cArgs.forEach { free($0) } }

            var argv = cArgs
            let argc = Int32(cArgs.count)
            let ret = node_start(argc, &argv)
            nodeExitCode = ret
            NSLog("[Empress] node_start exited with code %d", ret)
        }
    }
}

/// 游戏容器页：启动 Node 服务端后，用 WKWebView 加载本地游戏前端。
final class GameViewController: UIViewController {

    private var webView: WKWebView!
    private let statusLabel = UILabel()

    override var supportedInterfaceOrientations: UIInterfaceOrientationMask {
        // 游戏为横屏玩法（战斗画布 1200x760）
        return .landscape
    }

    override var prefersStatusBarHidden: Bool { true }

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = UIColor(red: 20/255, green: 23/255, blue: 38/255, alpha: 1)

        setupStatusLabel()
        setupWebView()

        let gameDir = Bundle.main.resourcePath! + "/game-data"
        let saveDir = documentsPath() + "/empress-profile"
        NodeRunner.start(gameDir: gameDir, saveDir: saveDir)
        waitForServer(attemptsLeft: 120) { [weak self] in
            self?.loadGame()
        }
    }

    private func documentsPath() -> String {
        let urls = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)
        return urls[0].path
    }

    private func setupStatusLabel() {
        statusLabel.text = "启动游戏引擎…"
        statusLabel.textColor = .white
        statusLabel.textAlignment = .center
        statusLabel.font = UIFont.systemFont(ofSize: 17, weight: .medium)
        statusLabel.numberOfLines = 0
        statusLabel.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(statusLabel)
        NSLayoutConstraint.activate([
            statusLabel.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            statusLabel.centerYAnchor.constraint(equalTo: view.centerYAnchor),
            statusLabel.leadingAnchor.constraint(greaterThanOrEqualTo: view.leadingAnchor, constant: 24),
            statusLabel.trailingAnchor.constraint(lessThanOrEqualTo: view.trailingAnchor, constant: -24)
        ])
    }

    private func setupWebView() {
        let config = WKWebViewConfiguration()
        config.allowsInlineMediaPlayback = true
        if #available(iOS 14.0, *) {
            config.mediaTypesRequiringUserActionForPlayback = []
        } else {
            config.mediaTypesRequiringUserActionForPlayback = .audio
        }
        config.websiteDataStore = .default()

        webView = WKWebView(frame: .zero, configuration: config)
        webView.translatesAutoresizingMaskIntoConstraints = false
        webView.isHidden = true
        webView.scrollView.bounces = false
        view.addSubview(webView)
        NSLayoutConstraint.activate([
            webView.topAnchor.constraint(equalTo: view.topAnchor),
            webView.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            webView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            webView.trailingAnchor.constraint(equalTo: view.trailingAnchor)
        ])
    }

    private func waitForServer(attemptsLeft: Int, completion: @escaping () -> Void) {
        guard attemptsLeft > 0 else {
            showDiagnostics()
            return
        }
        let url = URL(string: "http://127.0.0.1:3210/api/health")!
        var request = URLRequest(url: url)
        request.timeoutInterval = 2

        URLSession.shared.dataTask(with: request) { [weak self] data, _, error in
            guard let self = self else { return }
            if let error = error {
                NodeRunner.lastHealthError = error.localizedDescription
            }
            if let data = data,
               let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
               obj["ok"] as? Bool == true {
                DispatchQueue.main.async { completion() }
            } else {
                DispatchQueue.main.async {
                    self.waitForServer(attemptsLeft: attemptsLeft - 1, completion: completion)
                }
            }
        }.resume()
    }

    /// 纯 socket 直连探测 127.0.0.1:port（绕开 URLSession/ATS，判断 server 是否真的在监听）
    private func tcpProbe(port: Int, timeout: Double) -> String {
        var addr = sockaddr_in()
        addr.sin_family = sa_family_t(AF_INET)
        addr.sin_port = in_port_t(port).bigEndian
        addr.sin_addr.s_addr = inet_addr("127.0.0.1")
        let fd = socket(AF_INET, SOCK_STREAM, 0)
        guard fd >= 0 else { return "socket 创建失败" }
        defer { close(fd) }
        var flags = fcntl(fd, F_GETFL, 0)
        _ = fcntl(fd, F_SETFL, flags | O_NONBLOCK)
        let rc = withUnsafePointer(to: &addr) { ptr in
            ptr.withMemoryRebound(to: sockaddr.self, capacity: 1) { sp in
                connect(fd, sp, socklen_t(MemoryLayout<sockaddr_in>.size))
            }
        }
        if rc == 0 { return "端口可达(已连接)" }
        if errno != EINPROGRESS {
            let e = String(cString: strerror(errno))
            return "连接被拒绝: " + e
        }
        var waited: Double = 0
        while waited < timeout {
            usleep(200_000)
            waited += 0.2
            var err: Int32 = 0
            var errLen = socklen_t(MemoryLayout<Int32>.size)
            let g = getsockopt(fd, SOL_SOCKET, SO_ERROR, &err, &errLen)
            if g == 0 && err == 0 { return "端口可达(已连接)" }
            if g == 0 && err != 0 {
                let e = String(cString: strerror(err))
                return "连接被拒绝: " + e
            }
        }
        return "端口不可达(超时)"
    }

    /// 健康检查超时：把引擎启动的关键诊断直接显示在界面上，便于截图定位。
    private func showDiagnostics() {
        statusLabel.font = UIFont.monospacedSystemFont(ofSize: 12, weight: .regular)
        statusLabel.textAlignment = .left

        var lines = ["游戏引擎启动失败", ""]
        let elapsed = Int(Date().timeIntervalSince(NodeRunner.startTime))
        lines.append("已等待: " + String(elapsed) + " 秒")
        let gameDir = Bundle.main.resourcePath! + "/game-data"
        let fm = FileManager.default
        lines.append("app 包: " + (Bundle.main.resourcePath ?? "?"))
        lines.append("game-data: " + (fm.fileExists(atPath: gameDir) ? "存在" : "不存在"))
        lines.append("server: " + (fm.fileExists(atPath: gameDir + "/server/index.cjs") ? "存在" : "不存在"))
        lines.append("client: " + (fm.fileExists(atPath: gameDir + "/client/index.html") ? "存在" : "不存在"))
        let saveDir = NodeRunner.saveDirPath
        lines.append("存档目录: " + (fm.fileExists(atPath: saveDir) ? "存在" : "不存在"))
        lines.append("socket探测 3210: " + tcpProbe(port: 3210, timeout: 3))
        if let e = NodeRunner.lastHealthError {
            lines.append("健康检查错误: " + e)
        }
        let logPath = saveDir + "/empress-node.log"
        if let content = try? String(contentsOfFile: logPath, encoding: .utf8), !content.isEmpty {
            lines.append("node 日志(" + String(content.count) + " 字符):")
            let tail = content.suffix(600)
            lines.append(String(tail))
        } else {
            lines.append("node 日志: 不存在或为空")
        }
        if let code = NodeRunner.nodeExitCode {
            lines.append("node_start 退出码: " + String(code))
        } else {
            lines.append("node_start: 尚未返回（仍在初始化）")
        }
        statusLabel.text = lines.joined(separator: "\n")
    }

    private func loadGame() {
        statusLabel.isHidden = true
        webView.isHidden = false
        if let url = URL(string: "http://127.0.0.1:3210/") {
            webView.load(URLRequest(url: url))
        }
    }
}
