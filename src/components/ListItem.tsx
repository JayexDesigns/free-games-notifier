import {useState} from "react";
import {emit} from "@tauri-apps/api/event";
import "./ListItem.css";

type ListItemProps = {
	id: String;
	title: String;
	url: String;
	initialViewed: Boolean;
};

function ListItem({id, title, url, initialViewed}: ListItemProps) {
	const [viewed, setViewed] = useState(initialViewed);

	const changeViewed = async (newVal: Boolean) => {
		setViewed(newVal);
		await emit("change_viewed", {id, viewed: newVal});
	};

	return (
		<div className={`listItem ${viewed ? "viewed" : "notViewed"}`}>
			<div className="listItemData">
				<h2>{title}</h2>
				<h3>{url}</h3>
			</div>
			<div className="listItemControls">
				<button className="button" onClick={() => changeViewed(!viewed)}>
					Set as {viewed ? "not" : ""} seen
				</button>
				<a className="button" href={url as string} target="_blank" rel="noreferrer" onClick={() => changeViewed(true)}>
					Open website
				</a>
			</div>
		</div>
	);
}

export default ListItem;
