% rebase('base.tpl', title='Blog posts', current_page='blog')
<ul>
    % for post in posts:
    <li>
        <aside class="dates">{{post['date']}}</aside>
        <a href="{{post['path']}}">{{post['title']}}</a></li>
</ul>

  <!--- Uncomment for link to archive.
  {% if posts|length >= 4 %}
  <footer id="post-list-footer">
    <a id="archive-link" href="archive.html"> <span class="arrow">&larr;</span> Archive</a>
  </footer>
  {% endif %}
  --->