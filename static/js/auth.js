async function Register(){
    var email = document.getElementById('email').value
    var password = document.getElementById('password').value;
    var confirmPassword = document.getElementById('confirmPassword').value
    var role = document.getElementById('role').value

    var res = await fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json'},
        body: JSON.stringify({email: email, password: password, role: role, confirmPassword: confirmPassword})
    })

    var data = await res.json();
    if( res.ok){
        window.location.href = '/login'
    }else{
        console.log(data.error)
    }
}

async function Login(){
    var email = document.getElementById('email').value
    var password = document.getElementById('password').value;

        var res = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json'},
        body: JSON.stringify({email: email, password: password})
    })

    var data = await res.json();

    
    if( res.ok){
        window.location.href = '/dashboard'
    }else{
        console.log(data.error)
    }
}

function showMessage(containerId, type, text) {
    var div = document.getElementById(containerId);

    var alert = document.createElement('div');
    alert.className = 'alert' + type;
    alert.innerHTML = text;

    div.innerHTML = '';
    div.appendChild(alert);
}



async function Forgot() {
    var email = document.getElementById('email').value;

    var res = await fetch('/api/forgot-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email })
    });
    var data = await res.json();

    if (res.ok) {
        var messageText = document.createTextNode(data.message);

        var br1 = document.createElement('br');
        var br2 = document.createElement('br');

        var linkLabel = document.createElement('b');
        linkLabel.textContent = 'Link: ';

        var anchor = document.createElement('a');
        anchor.href = data.reset_link;
        anchor.textContent = data.reset_link;

        var br3 = document.createElement('br');

        var tokenLabel = document.createElement('b');
        tokenLabel.textContent = 'Token: ';

        var tokenText = document.createTextNode(data.token);

        var wrapper = document.createElement('span');
        wrapper.appendChild(messageText);
        wrapper.appendChild(br1);
        wrapper.appendChild(br2);
        wrapper.appendChild(linkLabel);
        wrapper.appendChild(anchor);
        wrapper.appendChild(br3);
        wrapper.appendChild(tokenLabel);
        wrapper.appendChild(tokenText);

        var container = document.getElementById('message');
        container.innerHTML = '';

        var alert = document.createElement('div');
        alert.className = 'alert';
        alert.appendChild(wrapper);

        container.appendChild(alert);
    } else {
        showMessage('message', 'error', data.error);
    }
}

async function Reset(token) {
    var newPassword = document.getElementById('new_password').value;

    var res = await fetch('/api/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: token, new_password: newPassword })
    });
    var data = await res.json();

    if (res.ok) {
        showMessage('message', 'success', data.message);
        window.location.href = '/login'
    } else {
        showMessage('message', 'error', data.error);
    }
}

