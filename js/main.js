// ★jqueryはアニメーションとプラグインのみに使用する


// スタイルとかで使う定数群
var VP = {
    FORM_HEIGHT : '128px',
};

Object.freeze(VP);

var pains = [];
var remarks = [];
var ws;

var init = function(){
    ws = new WebSocket(CHAT.url);
    ws.open = function(){ws.send('main;' + CHAT.user + ';hi');};
    ws.onmessage = function(e){
      var ds = e.data.split(';');
      var room;
      var user = ds[0];
      var text = "";
      ds.slice(1).forEach(function(d){
        var s = d[0];
        if (s==='#' && !room) {
          room = d.slice(1);
        } else {
          text += d;
        }
      });
      remarks.push({room:room, user:user, text:text});
      addRemark(room, user, text);
    };
    addEnterButton();
    addPain("main");
};

var addEnterButton = function() {
    var dEnter = document.querySelector('#Enter');
    if (dEnter) return;
    var dMain = document.querySelector('#Main'); 
    dEnter = document.createElement("img");
    dEnter.id = 'Enter';
    dEnter.src = 'img/enter.png';
    dEnter.addEventListener('click', showRoomList);
    dMain.appendChild(dEnter);
};


var addPain = function(roomName) {
    if (pains.map(function(p){return p.dataset.name}).indexOf(roomName) !== -1){ return;}

    var dMain = document.querySelector('#Main'); 
    var dPain = document.createElement('div');
    dPain.classList.add('room');
    dPain.dataset.name = roomName;
    dMain.appendChild(dPain);
    pains.push(dPain);

    resizePains();
    // Title
    var dCap = document.createElement('h1');
    dCap.innerText = roomName;
    dPain.appendChild(dCap);

    // Leave Button
    if(pains.length > 1) {
        dPain.appendChild(createRoomLeave(roomName));
    }
    dPain.appendChild(createRoomRemarks(dPain));
    dPain.appendChild(createRoomForm(roomName, CHAT.user));
    dPain.querySelector('textarea').focus();

    // Set previous remarks
    remarks.filter(function(x){return x.room == roomName}).forEach(function(x){
        addRemark(x.room, x.user, x.text);
    });
}

var resizePains = function(dMain) {
    var dMain = document.querySelector('#Main'); 
    var dEnter = document.querySelector('#Enter');
    var w = (dMain.offsetWidth - 64) / pains.length;
    pains.forEach(function(p, i){
        p.style.bottom = '1em';
        p.style.top = '1em';
        $(p).animate({left:(w * i + 8) + 'px', width:(w - 16) + 'px'}, 250);
    });
    // button for entering a room
    var x = w * pains.length - 4;
    $(dEnter).animate({left : x + 'px'}, 250);
};

var createRoomLeave = function(roomName) {
    var d = document.createElement('img');
    d.src = 'img/leave.png';
    d.dataset.room = roomName;
    d.classList.add('room-leave');
    d.style.zIndex = 200;
    var f = function() {
      var target = document.querySelector('div[data-name="'+this.dataset.room+'"]');
      pains = pains.filter(function(x){return x != target});
      target.parentNode.removeChild(target);
      resizePains();
    };
    d.addEventListener('click', f.bind(d), false);
    return d;
}

var createRoomRemarks = function() {
    var d = document.createElement('div');
    d.classList.add('room-remarks');
    d.style.top = '48px';
    d.style.bottom = VP.FORM_HEIGHT;
    d.style.left = '0';
    d.style.right = '-24px';
    return d;
};

var createRoomForm = function(roomName, userName) {
    var d = document.createElement('div');
    d.classList.add('room-form');
    d.style.height = VP.FORM_HEIGHT;
    d.style.bottom = '0';
    d.style.left = '0';
    d.style.right = '0';
    var dInput = document.createElement('textarea');
    dInput.classList.add('input');
    dInput.dataset.room = roomName;

    var f = function(e){
        if (e.keyCode !== 13) return true;
        e.preventDefault();
        if (this.value.trim().length == 0) return false;
        sendRemark(this);
        this.value = "";
        return false;
    };
    
    dInput.addEventListener('keydown', f, false);
    d.appendChild(dInput);
    return d;
};

var sendRemark = function(form) {
    ws.send([CHAT.user, '#' + form.dataset.room, form.value].join(';'));
}

var addRemark = function(room, name, text) {
    var dRemarkArea = document.querySelector('div[data-name="'+room+'"] .room-remarks');
    if (!dRemarkArea) return;
    var dRemark = document.createElement('div');
    var dName = document.createElement('span');
    var dText = document.createElement('div');
    
    dRemark.classList.add('remark');

    dName.classList.add('remark-name');
    dName.innerText = name;
    dText.classList.add('remark-text');
    dText.innerText = text;
    $(dText).css({opacity:0});
    dRemark.appendChild(dName);
    dRemark.appendChild(dText);
    
    dRemarkArea.appendChild(dRemark);
    // Visual Effects
    // Scroll
    var h = Number(dRemarkArea.dataset.height) || 0;
    dRemarkArea.dataset.height = h + dRemark.clientHeight;
    $(dRemarkArea).animate({scrollTop:h + 'px'}, 'slow');
    // Name Animation
    $({deg:30}).animate({deg:-15}, {
        duration:500,
        easing:'easeOutBounce',
        progress:function(){$(dName).css({transform:'rotate(' + this.deg + 'deg)'});}
    });
    // Text Animation
    $(dText).animate({opacity:1}, 1000);
};

var showRoomList = function() {
    var shown = pains.map(function(p){return p.dataset.name});
    var rs = remarks.map(function(x){return x.room}).filter(function(x, i, xs){return xs.indexOf(x) === i && shown.indexOf(x) === -1});
    
    // BackGround
    var dRListBack = document.createElement('div');
    dRListBack.id = 'RoomListBack';
    dRListBack.addEventListener('click', hideRoomList, false);
    $(dRListBack).css({opacity:0});

    // ListArea
    var dListArea = document.createElement('div');
    dListArea.id = 'RoomListArea';

    // Room Links
    var dLinks = document.createElement('div');
    dLinks.id = 'RoomListLinks';
    rs.forEach(function(r){
        var dLink = document.createElement('a');
        dLink.innerText = r;
        dLink.dataset.target = r;
        dLinks.appendChild(dLink);
        var f = function() {
            addPain(this.dataset.target);
        };
        dLink.addEventListener('click', f.bind(dLink));
    });
    dListArea.appendChild(dLinks);
    
    // New Room
    var dInput = document.createElement('input');
    dInput.placeholder = 'room name';
    var fClick = function(e) {
        e.stopPropagation();
    };

    var fEnter = function(e) {
        if (e.keyCode !== 13) return true;
        var name = this.value.trim();
        if (name.length == 0) return true;
        e.preventDefault();
        addPain(name);
        hideRoomList();
    };
    dInput.addEventListener('click', fClick, false);
    dInput.addEventListener('keydown', fEnter.bind(dInput), false);
    dListArea.appendChild(dInput);

    dRListBack.appendChild(dListArea);
    // Show
    document.body.appendChild(dRListBack);
    $(dRListBack).animate({opacity : 1}, 250, function(){dInput.focus();});
};

var hideRoomList = function() {
    var dRListBack = document.querySelector('#RoomListBack');
    if(!dRListBack) return;
    var f = function() {
        dRListBack.parentNode.removeChild(dRListBack);
        delete dRListBack;
    };
    $(dRListBack).animate({opacity:0}, 200, f);
};

$(init);
