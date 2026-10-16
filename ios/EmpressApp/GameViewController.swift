import Foundation
import WebKit

/// 启动内嵌 Node.js 运行时（nodejs-mobile 的 node_start），在独立线程中运行游戏服务端。
final class NodeRunner {

    /// 阻塞调用 node_start 并常驻事件循环，必须在后台线程执行。
    /// - Parameters:
    ///   - gameDir: 打包进 App 的 game-data 目录绝对路径
    ///   - saveDir: 存档目录绝对路径（App Documents 下）
    static func start(gameDir: String, saveDir: String) {
        let script = gameDir + "/android-bootstrap.cjs"
        let arguments = ["node", script, gameDir, saveDir]

        // 重定向 Node 的 stdout/stderr 到存档目录日志文件：
        // iOS 上 Node 的 console 默认无处可去，启动失败原因会静默丢失，
        // 写文件后可通过 Documents/empress-node.log 直接定位。
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
        statusLabel.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(statusLabel)
        NSLayoutConstraint.activate([
            statusLabel.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            statusLabel.centerYAnchor.constraint(equalTo: view.centerYAnchor)
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
            statusLabel.text = "游戏引擎启动失败"
            return
        }
        let url = URL(string: "http://127.0.0.1:3210/api/health")!
        var request = URLRequest(url: url)
        request.timeoutInterval = 2

        URLSession.shared.dataTask(with: request) { [weak self] data, _, _ in
            guard let self = self else { return }
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

    private func loadGame() {
        statusLabel.isHidden = true
        webView.isHidden = false
        if let url = URL(string: "http://127.0.0.1:3210/") {
            webView.load(URLRequest(url: url))
        }
    }
}
