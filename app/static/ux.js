document.addEventListener('DOMContentLoaded',()=>{
  const links=[...document.querySelectorAll('.sidebar nav a')];
  const sections=links.map(a=>document.querySelector(a.getAttribute('href'))).filter(Boolean);
  const activate=()=>{let current=sections[0];for(const s of sections){if(s.getBoundingClientRect().top<=140)current=s}links.forEach(a=>a.classList.toggle('active',a.getAttribute('href')==='#'+current.id))};
  window.addEventListener('scroll',activate,{passive:true});activate();

  const labels={'Needs review':'דורש בדיקה','Requested':'בקשת הסרה','Removed':'הוסר','Unknown':'לא ידוע','Canceled':'בוטל','Support required':'נדרשת תמיכה'};
  document.querySelectorAll('.service-state,.tag').forEach(el=>{const text=el.textContent.trim();if(labels[text])el.textContent=labels[text];});

  const cleanup=document.querySelector('#cleanup .service-list');
  const services=document.querySelector('#services');
  if(cleanup||services){
    const bar=document.createElement('div');bar.className='ux-tools';
    bar.innerHTML='<div class="search-box"><span>⌕</span><input type="search" aria-label="חיפוש שירות" placeholder="חיפוש שירות, קטגוריה או 4 ספרות…"></div><div class="filter-pills"><button type="button" class="filter-pill active" data-filter="all">הכול</button><button type="button" class="filter-pill" data-filter="Needs review">דורש בדיקה</button><button type="button" class="filter-pill" data-filter="Requested">בטיפול</button><button type="button" class="filter-pill" data-filter="Removed">הוסר</button></div>';
    const target=cleanup?.closest('.panel')||services;target.querySelector('.panel-head')?.after(bar);
    const input=bar.querySelector('input');const pills=[...bar.querySelectorAll('.filter-pill')];
    const apply=()=>{
      const q=input.value.trim().toLowerCase();const filter=bar.querySelector('.filter-pill.active')?.dataset.filter||'all';
      document.querySelectorAll('.service-row').forEach(row=>{const text=row.textContent.toLowerCase();const raw=row.querySelector('.service-state')?.textContent.trim()||'';const okSearch=!q||text.includes(q);const okFilter=filter==='all'||raw===labels[filter]||raw===filter;row.hidden=!(okSearch&&okFilter);});
      document.querySelectorAll('#services tbody tr').forEach(row=>{const text=row.textContent.toLowerCase();const tag=row.querySelector('.tag');const raw=tag?.textContent.trim()||'';row.hidden=!!(tag&&(!(!q||text.includes(q))||!(filter==='all'||raw===labels[filter]||raw===filter)));});
    };
    input.addEventListener('input',apply);pills.forEach(p=>p.addEventListener('click',()=>{pills.forEach(x=>x.classList.remove('active'));p.classList.add('active');apply()}));
  }

  document.querySelectorAll('form').forEach(form=>form.addEventListener('submit',e=>{
    const button=form.querySelector('button[type="submit"],button');
    if(button&&/הוסר/.test(button.textContent)&&!window.confirm('לסמן את השירות כהוסר?')){e.preventDefault();return}
    if(button){button.disabled=true;button.dataset.originalText=button.textContent;button.textContent='מבצע…'}
  }));
});
