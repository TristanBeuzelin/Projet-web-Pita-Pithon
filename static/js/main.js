

window.addEventListener("DOMContentLoaded", (event) => {
    
    var socket = io.connect("http://" + document.domain + ":" + location.port );

    
    


    document.onkeydown = function(e){
        switch(e.keyCode){
            case 37:
                socket.emit("move", {dx:-1, dy:0});
                break;
            case 38:
                socket.emit("move", {dx:0, dy:-1});
                break;
            case 39:
                socket.emit("move", {dx:1, dy:0});
                break;
            case 40:
                socket.emit("move", {dx:0, dy:1});
                break;
            /*Ajout*/
            case 32:
                /* Essayer de coder l'attaque ici */
                function attack(){
                    var player_position = document.getElementById()
                }
                socket.emit("attack") 
            /******/
        }


    };
    
    var btn_n = document.getElementById("go_n");
    btn_n.onclick = function(e) {
        console.log("Clicked on button north");
        socket.emit("move", {dx:0, dy:-1});
    };

    var btn_s = document.getElementById("go_s");
    btn_s.onclick = function(e) {
        console.log("Clicked on button south");
        socket.emit("move", {dx:0, dy:1});
    };

    var btn_w = document.getElementById("go_w");
    btn_w.onclick = function(e) {
        console.log("Clicked on button w");
        socket.emit("move", {dx:-1, dy:0});
    };

    var btn_e = document.getElementById("go_e");
    btn_e.onclick = function(e) {
        console.log("Clicked on button e");
        socket.emit("move", {dx:1, dy:0});
    };
    var retry_btn = document.getElementById("retry");
    retry_btn.onclick = function() {
        socket.emit("reset");
        var game_over = document.getElementById("game_over");
        game_over.style.display = 'none';
        var retry = document.getElementById("retry");
        retry.style.display = 'none';
        var div_to_hide = document.getElementById("flexbox");
        div_to_hide.style.display = 'flex';
        var golds_td = document.getElementById("golds");
        golds_td.textContent = 0;
        var HP_td = document.getElementById("hp");
        HP_td.textContent = 100;
    };

    function component(color, x, y) {
        var res = 18;
        ctx = myGameArea.context;
        ctx.fillStyle = color;
        ctx.fillRect(x*res, y*res, width, height);
    }

        socket.on("response", function(data){
        console.log(data);
        var colors = ["white","blue"]
        for( var i=0; i<2; i++){
            var pos_x = data[i].j;
            var pos_y = data[i].i;
            component(color[i],pos_x,pos_y)
        }
        /*Ajout*/
        var golds_td = document.getElementById("golds")
        golds_td.textContent = data[2]
        var HP_td = document.getElementById("hp")
        HP_td.textContent = data[3]
        if( data[3] == 0 )
        {
            var div_to_hide = document.getElementById("flexbox")
            div_to_hide.style.display = 'none';
            var game_over = document.getElementById("game_over");
            game_over.style.display = 'flex';
            var retry = document.getElementById("retry");
            retry.style.display = 'flex';
        }
        /*******/
    });
});