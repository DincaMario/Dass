async function loadAuditLogs() {
    var res = await fetch('/api/audit-logs');
    if (res.status == 401)
    {
        window.location.href = "/login";
        return
    }
    var logs = await res.json();
    var tbody = document.getElementById('audit-table');

    tbody.innerHTML = '';

    for (var i = 0; i < logs.length; i++) {
        var log = logs[i];
        var tr = document.createElement('tr');
        var fields = [log.timestamp, log.user_id, log.action, log.resource, log.resource_id, log.ip_address, log.details];

        for (var j = 0; j < fields.length; j++) {
            var td = document.createElement('td');
            td.textContent = fields[j] != null && fields[j] !== '' ? fields[j] : '—';
            tr.appendChild(td);
        }

        tbody.appendChild(tr);
    }
}

loadAuditLogs()