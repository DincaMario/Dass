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