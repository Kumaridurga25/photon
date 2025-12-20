const WS_URL = "ws://127.0.0.1:8000/ws";
const statusEl=document.getElementById("status");
const container=document.getElementById("stocks-container");

let previousPrices={};

const socket = new WebSocket(WS_URL)

socket.onopen=()=>{
    statusEl.textContent = "Connected";
}

socket.onclose=()=>{
    statusEl.textContent="Disconnected";
}

socket.onerror=()=>{
    statusEl.textContent="Error";
}

socket.onmessage = (event) =>{
    const data = JSON.parse(event.data);

    if (Array.isArray(data)){
        data.forEach(item =>{
            updateStock(item.ticker, item.price);
        });
    }else{
        updateStock(data.ticker, data.price)
    }
};

function updateStock(ticker, price){
    let card=document.getElementById(ticker)

    if (!card){
        card=document.createElement("div");
        card.className="stock-card";
        card.id=ticker;

        card.innerHTML=`
        <div class="stock-name">${ticker}</div>
        <div class="stock-price">${price}</div>
        `

        container.appendChild(card);
    }

    const priceEl=card.querySelector(".stock-price");

    if (previousPrices[ticker] !== undefined){
        if (price > previousPrices[ticker]){
            priceEl.className="stock-price up";
        }else if (price < previousPrices[ticker]){
            priceEl.className="stock-price down";
        }
    }

    priceEl.textContent=price;
    previousPrices[ticker]=price;
}


