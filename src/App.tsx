import {emit, listen} from "@tauri-apps/api/event";
import {isPermissionGranted, requestPermission, sendNotification} from "@tauri-apps/api/notification";
import {useState, useEffect} from "react";
import ListItem from "./components/ListItem";
import SettingsIcon from "./components/SettingsIcon";
import "./App.css";

type Game = {
	id: string;
	title: string;
	url: string;
	viewed: boolean;
};

type Notification = {
	title: string;
	body: string;
};

function App() {
	const [gamesList, setGamesList] = useState<Array<Game>>([]);
	const [settingsOpened, setSettingsOpened] = useState(false);

	useEffect(() => {
		const initializeListeners = async () => {
			await listen("send_list", ({payload}) => {
				setGamesList(payload as Array<Game>);
			});

			let permissionGranted = await isPermissionGranted();
			if (!permissionGranted) {
				const permission = await requestPermission();
				permissionGranted = permission === "granted";
			}
			if (permissionGranted) {
				await listen("notificate", ({payload}) => {
					let {title, body} = payload as Notification;
					sendNotification({title, body, icon: "/icons/icon.png", sound: "default"});
				});
			}

			emit("get_list");
		};
		initializeListeners();
	}, []);

	return (
		<div className="app">
			<section className="notifications">
				<div className="header">
					<h1>Notification List</h1>
					<div>
						<button onClick={() => setSettingsOpened(prev => !prev)}>
							<SettingsIcon />
						</button>
						<div className={`settings ${settingsOpened ? "show" : "hide"}`}>
							<label>
								<input type="checkbox" />
								Start on startup
							</label>
							<hr />
							<button>Exit</button>
						</div>
					</div>
				</div>
				<ul className="list">
					{gamesList.map(game => (
						<ListItem key={game.id} id={game.id} title={game.title} url={game.url} initialViewed={game.viewed} />
					))}
				</ul>
			</section>
			<footer>
				<p>
					Made with ❤️ by{" "}
					<a href="https://jayex.design" target="_blank">
						Jayex Designs
					</a>
				</p>
				<p>
					<a href="https://github.com/JayexDesigns/free-games-notifier" target="_blank">
						Source code
					</a>
				</p>
			</footer>
		</div>
	);
}

export default App;
