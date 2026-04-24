var token = document.cookie.split('session_token=')[1];
async function loadTickets() {
    var res = await fetch('/api/tickets');
    var tickets = await res.json();
    renderTickets(tickets);
}

async function searchTickets() {
    var q = document.getElementById('search-q').value;
    var res = await fetch('/api/tickets/search?q=' + encodeURIComponent(q));
    var tickets = await res.json();
    renderTickets(tickets);
}


function renderTickets(tickets) {
    var tbody = document.getElementById('tickets-table');
    tbody.innerHTML = '';

    for (var i = 0; i < tickets.length; i++) {
        var t = tickets[i];

        var row = document.createElement('tr');

        var tdId = document.createElement('td');
        tdId.textContent = t.id;

        var tdTitle = document.createElement('td');
        tdTitle.textContent = t.title;

        var badge = document.createElement('span');
        badge.className = 'badge' + t.severity.toLowerCase();
        badge.textContent = t.severity;

        var tdSeverity = document.createElement('td');
        tdSeverity.appendChild(badge);

        var tdStatus = document.createElement('td');
        tdStatus.textContent = t.status;

        var editBtn = document.createElement('button');
        editBtn.className = 'btn btn-primary';
        editBtn.textContent = 'Edit';
        editBtn.onclick = (function(id) {
            return function() { editTicket(id); };
        })(t.id);

        var deleteBtn = document.createElement('button');
        deleteBtn.className = 'btn btn-danger';
        deleteBtn.textContent = 'Sterge';
        deleteBtn.onclick = (function(id) {
            return function() { deleteTicket(id); };
        })(t.id);

        var tdActions = document.createElement('td');
        tdActions.appendChild(editBtn);
        tdActions.appendChild(document.createTextNode(' '));
        tdActions.appendChild(deleteBtn);

        row.appendChild(tdId);
        row.appendChild(tdTitle);
        row.appendChild(tdSeverity);
        row.appendChild(tdStatus);
        row.appendChild(tdActions);

        tbody.appendChild(row);
    }
}


async function createTicket() {
    var title = document.getElementById('t-title').value;
    var description = document.getElementById('t-desc').value;
    var severity = document.getElementById('t-severity').value;

    var res = await fetch('/api/tickets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: title, description: description, severity: severity })
    });
    var data = await res.json();

    if (res.ok) {
        showMessage('ticket-message', 'success', data.message);
        document.getElementById('t-title').value = '';
        document.getElementById('t-desc').value = '';
        loadTickets();
    } else {
        showMessage('ticket-message', 'error', data.error);
    }
}


async function editTicket(id) {
    var newStatus = prompt('Noul status (OPEN / IN_PROGRESS / RESOLVED):');
    if (!newStatus) return;
    await fetch('/api/tickets/' + id, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
    });
    if (res.status === 403) alert('Acces interzis – nu esti proprietarul ticketului');
    loadTickets();
}

async function deleteTicket(id) {
    if (!confirm('Sigur vrei sa stergi acest ticket?')) return;
    await fetch('/api/tickets/' + id, { method: 'DELETE' });
    if (res.status === 403) alert('Acces interzis – nu esti proprietarul ticketului');
    loadTickets();
}


loadTickets();
