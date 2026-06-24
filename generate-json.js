const fs = require("fs");

const playlist = fs.readFileSync("IPtv", "utf8");

const lines = playlist.split("\n");

const result = {
  "Group Viva": [],
  "Group Event": []
};

for(let i = 0; i < lines.length; i++){

  const line = lines[i].trim();

  if(!line.startsWith("#EXTINF")) continue;

  const stream = lines[i + 1]?.trim();

  if(!stream) continue;

  const name =
    line.split(",").pop()?.trim() || "Unknown";

  const logoMatch =
    line.match(/tvg-logo="([^"]+)"/);

  const groupMatch =
    line.match(/group-title="([^"]+)"/);

  const logo =
    logoMatch ? logoMatch[1] : "";

  const group =
    groupMatch ? groupMatch[1] : "Unknown";

  const item = {
    name,
    logo,
    stream,
    group
  };

  if(group === "Group Viva"){
    result["Group Viva"].push(item);
  }
  else if(group === "Group Event"){
    result["Group Event"].push(item);
  }
}

fs.writeFileSync(
  "channels.json",
  JSON.stringify(result, null, 2)
);

console.log("channels.json generated");
