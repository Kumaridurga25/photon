const WS_URL = "ws://127.0.0.1:8000/ws"; // week-2 backend websocket
const statusEl = document.getElementById("status");
const container= document.getElementById("stocks-container");

let previousPrices = {};

//connect WebSocket
const socket = new WebSocket(WS_URL);

socket.onopen = () =>{
    statusEl.textContent="Connected";
};

socket.onclose=()=>{
    statusEl.textContent="Disconnected";
};

socket.onmessage=(event)=>{
    const data = JSON.parse(event.data);

    updateStockCard(data.ticker, data.price);
};

function updateStockCard(ticker, price){
    let card = document.getElementById(ticker);

    if (!card){
        card=document.createElement("div");
        card.className="stock-card";
        card.id=ticker;

        card.innerHTML=`
        <span class="name">${ticker}</span>
        <span class="value">${price}</span>
        `;

        container.appendChild(card)
    }

    //update price color based on increase/decrease

    let valueEl = card.querySelector(".value");

    if (previousPrices[ticker] !== undefined){
        if (price > previousPrices[ticker]){
            valueEl.className = "value green";
        }else if (price < previousPrices[ticker]){
            valueEl.className= "value red";
        }else{
            valueEl.className="value";
        }
    }

    // update UI with new price
    valueEl.textContent = price;

    //save for next comparison
    previousPrices[ticker]=price;
}