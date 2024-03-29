<%inherit file="base.mako"/>
<% from time import gmtime, asctime, time %>

<div class=grid_12>
<h2 id=page-heading>${trk['title']} Info</h2>
%if 'descr' in trk:
<p>${trk['descr']|h}</p>
%endif
<dl>
    <dt>Announce URL
    <dd>${trka|h}

%if trk.get('ssl', False):
    <dt>SSL Announce URL
    <dd>${trka.replace('http://', 'https://')|h}
%endif

%if trk.get('home', False):
    <dt>Homepage
    <dd><a href="${trk['home']|h}">${trk['home']|h}</a>
%endif

%if trk.get('alias', False):
    <dt>Announce URL aliases
    <dd><ul><li>${'<li>'.join(trk['alias'])}</ul>
%endif

%if trk.get('response', False):
    %if trk['response'].get('interval', False):
        <dt>Interval
        <dd>${trk['response']['interval']|h} seconds.
    %endif
    %if trk['response'].get('min interval', False):
        <dt>Minimum interval
        <dd>${trk['response']['min interval']|h} seconds.
    %endif
%endif

%if trk.get('error', False):
    <dt>Error
    <dd>${trk['error']|h}
%endif

%if trk.get('next-check', False):
    <dt>Next check scheduled in...
    <dd>${(trk['next-check']-int(time()))/60|h} minutes.
%endif

%if trk.get('next-check', False):
    <dt>Last performend check was...
    <dd>${(int(time())-logs[0]['updated'])/60|h} minutes ago.
%endif

</dl>

<table>
    <thead><tr>
        <th>Time
        <th>Latency
        <th>Error
    </tr></thead>
%for l in logs:
    <tr>
    <td class=center>${asctime(gmtime(l['updated']))[:-5]} UTC
    <td class=right>${"%.6f"%l['latency']}
    <td>${l.get('error','Just fine!')}
    </tr>
%endfor
</table>

</div>


<%def name="title()">${trk['title']} - Tracker Info</%def>
