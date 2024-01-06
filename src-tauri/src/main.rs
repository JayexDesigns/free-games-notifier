#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::sync::{mpsc, Arc};
use std::process;
use tauri::{
	AppHandle,
	Manager,
	SystemTray,
	CustomMenuItem,
	SystemTrayMenu,
	SystemTrayEvent,
};
use serde::{Serialize, Deserialize};
use scraper::{Html, Selector};
use rusqlite::Connection;
use uuid::Uuid;

struct Event {
	name: &'static str,
	payload: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct NotificationPayload {
	title: String,
	body: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct ChangeViewedPayload {
	id: String,
	viewed: bool,
}

#[derive(Debug, Clone, Serialize)]
struct Game {
	id: String,
	title: String,
	url: String,
	viewed: bool,
}

fn send_list(app: Arc<AppHandle>, games_list: &Vec<Game>) {
	app.emit_all("send_list", games_list).unwrap();
}

fn notificate(app: Arc<AppHandle>, notification: &NotificationPayload) {
	app.emit_all("notificate", notification).unwrap();
}

fn add_game(connection: &Connection, game: &Game) {
	connection.execute("INSERT INTO games (id, title, url, viewed) VALUES (?1, ?2, ?3, ?4)", (&game.id, &game.title, &game.url, game.viewed)).unwrap();
}

fn get_games(connection: &Connection) -> Vec<Game> {
	let mut statement = connection.prepare("SELECT * FROM games").unwrap();
	let games_iter = statement.query_map([], |row| {
		Ok(Game {
			id: row.get(0).unwrap(),
			title: row.get(1).unwrap(),
			url: row.get(2).unwrap(),
			viewed: row.get(3).unwrap(),
		})
	}).unwrap();

	let mut games = vec![];
	for game in games_iter {
		games.push(game.unwrap());
	}

	games.reverse();
	games
}

fn delete_game(connection: &Connection, id: &str) {
	connection.execute("DELETE FROM games WHERE id = ?1", (id,)).unwrap();
}

fn change_viewed(connection: &Connection, id: &str, viewed: bool) {
	connection.execute("UPDATE games SET viewed = ?1 WHERE id = ?2", (&viewed, id)).unwrap();
}


#[derive(Clone, Serialize)]
struct Payload {
	args: Vec<String>,
	cwd: String,
}

fn main() {
	let connection = Connection::open("games.db").unwrap();

	connection.execute("
		CREATE TABLE IF NOT EXISTS games (
			id TEXT PRIMARY KEY,
			title TEXT NOT NULL,
			url TEXT NOT NULL,
			viewed INTEGER NOT NULL
		)
	", ()).unwrap();

	let exit = CustomMenuItem::new("exit".to_string(), "Exit");
	let tray_menu = SystemTrayMenu::new().add_item(exit);
	let tray = SystemTray::new().with_menu(tray_menu);

	let app = tauri::Builder::default()
		.plugin(tauri_plugin_single_instance::init(|app, argv, cwd| {
			println!("{}, {argv:?}, {cwd}", app.package_info().name);
			app.emit_all("single-instance", Payload {args: argv, cwd}).unwrap();
			let window = app.get_window("main").unwrap();
			if !window.is_visible().unwrap() {
				window.show().unwrap();
				window.set_focus().unwrap();
			}
		}))
		.on_window_event(|event| {
			match event.event() {
				tauri::WindowEvent::CloseRequested {api, ..} => {
					event.window().hide().unwrap();
					api.prevent_close();
				}
				_ => {}
			}
		})
		.system_tray(tray)
		.on_system_tray_event(|app, event| match event {
			SystemTrayEvent::LeftClick {position: _, size: _, ..} => {
				let window = app.get_window("main").unwrap();
				if window.is_visible().unwrap() {
					window.hide().unwrap();
				}
				else {
					window.show().unwrap();
					window.set_focus().unwrap();
				}
			}
			SystemTrayEvent::MenuItemClick {id, ..} => {
				match id.as_str() {
					"exit" => {
						process::exit(0);
					}
					_ => {}
				}
			}
			_ => {}
		})
		.build(tauri::generate_context!())
		.expect("failed to run app");

	let (sender, receiver) = mpsc::channel::<Event>();
	let app_handle = Arc::new(app.handle().clone());
	tauri::async_runtime::spawn(async move {
		while let Ok(event) = receiver.recv() {
			if event.name == "get_list" {
				send_list(app_handle.clone(), &get_games(&connection));
			}
			else if event.name == "notificate" {
				let payload = serde_json::from_str::<NotificationPayload>(&event.payload).unwrap();
				notificate(app_handle.clone(), &payload);
			}
			else if event.name == "change_viewed" {
				let payload = serde_json::from_str::<ChangeViewedPayload>(&event.payload).unwrap();
				change_viewed(&connection, &payload.id, payload.viewed);
			}
			if event.name == "exit" {
				process::exit(0);
			}
		}
	});

	let sender_clone = sender.clone();
	app.listen_global("get_list", move |_event| {
		sender_clone.send(Event {name: "get_list", payload: String::from("")}).unwrap();
	});

	let sender_clone = sender.clone();
	app.listen_global("change_viewed", move |event| {
		if let Some(payload) = event.payload() {
			sender_clone.send(Event {name: "change_viewed", payload: payload.to_string()}).unwrap();
		}
	});

	let sender_clone = sender.clone();
	app.listen_global("exit", move |_event| {
		sender_clone.send(Event {name: "exit", payload: String::from("")}).unwrap();
	});

	let sender_clone = sender.clone();
	let connection = Connection::open("games.db").unwrap();
	tauri::async_runtime::spawn(async move {
		loop {
			let response = reqwest::get("https://www.indiegamebundles.com/category/free/").await.unwrap();
			let status = response.status();
			match status {
				reqwest::StatusCode::OK => {
					let selector = Selector::parse(".tdb_module_loop > div > div:nth-child(2) h3 a").unwrap();
					let document = Html::parse_document(&response.text().await.unwrap());

					let games_list = get_games(&connection);
					let mut elements_list: Vec<Game> = vec![];
					for element in document.select(&selector) {
						let game = Game {
							id: Uuid::new_v4().to_string(),
							title: element.inner_html(),
							url: element.attr("href").unwrap().to_string(),
							viewed: false
						};
						elements_list.push(game);
					}

					let mut updated = false;
					for element in elements_list.iter().rev() {
						if games_list.iter().any(|i| i.url == element.url) {
							continue;
						}
						add_game(&connection, &element);
						updated = true;
					}
					for game in &games_list {
						if elements_list.iter().any(|i| i.url == game.url) {
							continue;
						}
						delete_game(&connection, &game.id);
						updated = true;
					}

					if updated {
						sender_clone.send(Event {name: "get_list", payload: String::from("")}).unwrap();
						sender_clone.send(Event {name: "notificate", payload: serde_json::to_string(&NotificationPayload {
							title: String::from("New Game/Games"),
							body: String::from("New Free Game/Games Available"),
						}).unwrap()}).unwrap();
					}
				}
				_ => {}
			}
			std::thread::sleep(std::time::Duration::from_secs(60 * 5));
		}
	});

	app.run(|_app_handle, event| match event {
		tauri::RunEvent::ExitRequested { api, .. } => {
			api.prevent_exit();
		}
		_ => {}
	});
}
