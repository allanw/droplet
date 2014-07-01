% rebase('base.tpl', title='Blog posts')
<ul>
% for post in posts:
<li>{{post['date']}} <a href="{{post['path']}}">{{post['title']}}</a></li>
</ul>