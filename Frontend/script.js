const WS_URL = "ws://127.0.0.1:8000/ws";

const statusEl =document.getElementById("status")
const logBox = document.getElementById("log")
const input = document.getElementById("msgInput")
const sendBtn = document.getElementById("sendBtn")

let socket;

//function to print messages
function addLog(text){
    logBox.innerHTML += text + "<br>";
    logBox.scrollTop = logBox.scrollHeight;
}

//connect websocket
function connect(){
    socket = new WebSocket(WS_URL);

    socket.onopen = () => {
        statusEl.textContent = "connected";
        addLog("Connected to server");
    };

    socket.onclose = () =>{
        statusEl.textContent = "disconnected";
        addLog("Disconnected from server");
    };

    socket.onerror = (err)=>{
        statusEl.textContent="error";
        addLog("WebSocket error");
        console.error(err);
    };
}

//send message to server
sendBtn.addEventListener("click", ()=>{
    const msg = input.value.trim();
    if (!msg) return;

    if (socket.readyState === WebSocket.OPEN) {
        socket.send(msg);
        addLog("You: "+ msg);
        input.value="";
    }else{
        addLog("Socket not open - try again");
    }

});

connect();