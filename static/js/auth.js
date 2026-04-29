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
        showMessage('message', 'success', data.message);
        window.location.href = '/login'
    }else{
        console.log(data.error)
        showMessage('message', 'error', data.error);
    }
}


function showErrorWithDetails(containerId, error, details) {
    var html = '<div class="alert alert-error">' + error;
    if (details && details.length > 0) {
        html += '<ul>';
        for (var i = 0; i < details.length; i++) {
            html += '<li>' + details[i] + '</li>';
        }
        html += '</ul>';
    }
    html += '</div>';
    document.getElementById(containerId).innerHTML = html;
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
        showMessage('message', 'success', data.message);
        window.location.href = '/dashboard'
    }else{
        console.log(data.error)
        showMessage('message', 'error', data.error);
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

    showMessage('message', 'success', data.message);

    
    if (data.reset_link) {
        var msgDiv = document.getElementById('message');
        msgDiv.innerHTML += '<div class="alert" >'
            + 'Debug (lab): <a href="' + data.reset_link + '">' + data.reset_link + '</a></div>';
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

async function Logout() {
    await fetch('/api/logout', { method: 'POST' });
    window.location.href = '/login';
}