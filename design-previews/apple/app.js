const services = [
  {label:'ЗАЩИТА НА ПЕРСПЕКТИВУ', title:'Кузов под\nзащитой.', text:'Полная антикоррозионная обработка — чтобы влага, реагенты и время оставляли меньше следов на вашем автомобиле.'},
  {label:'СЕРДЦЕ ВАШЕГО АВТОМОБИЛЯ', title:'Двигатель\nв порядке.', text:'Квалифицированный ремонт двигателя. Расскажите о симптомах — обсудим состояние автомобиля и необходимые работы.'},
  {label:'УВЕРЕННОСТЬ НА КАЖДОМ ПОВОРОТЕ', title:'Держим\nдорогу.', text:'Ремонт ходовой части. Стуки, вибрации или изменения в поведении автомобиля — повод обратиться к мастерам.'},
  {label:'ДВИЖЕНИЕ БЕЗ ЛИШНИХ ВОПРОСОВ', title:'Передаём\nмощность.', text:'Ремонт трансмиссии. Уточним особенности вашего автомобиля, разберёмся в неисправности и обсудим объём работ.'},
  {label:'ВНИМАНИЕ К КАЖДОЙ ДЕТАЛИ', title:'Детали\nрешают.', text:'Все виды слесарных работ. Отдельная задача или комплексный ремонт — свяжитесь с нами, чтобы обсудить, что нужно вашему авто.'}
];
const tabs = [...document.querySelectorAll('.service-tab')];
function selectService(index, focus = false) {
  const data = services[index];
  tabs.forEach((tab,i) => { tab.classList.toggle('active', i === index); tab.setAttribute('aria-selected', String(i === index)); tab.tabIndex = i === index ? 0 : -1; });
  document.querySelector('.detail-label').textContent = data.label;
  const title = document.getElementById('service-title'); title.textContent = data.title; title.style.whiteSpace = 'pre-line';
  document.getElementById('service-description').textContent = data.text;
  document.getElementById('service-panel').setAttribute('aria-labelledby', `tab-${index}`);
  if (focus) tabs[index].focus();
}
tabs.forEach((tab,i) => {
  tab.addEventListener('click', () => selectService(i));
  tab.addEventListener('keydown', e => {
    let index;
    if (e.key === 'ArrowDown' || e.key === 'ArrowRight') index = (i+1)%tabs.length;
    if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') index = (i-1+tabs.length)%tabs.length;
    if (e.key === 'Home') index = 0;
    if (e.key === 'End') index = tabs.length-1;
    if (index !== undefined) { e.preventDefault(); selectService(index, true); }
  });
});
const dialog = document.getElementById('booking');
document.querySelectorAll('.booking-trigger').forEach(button => button.addEventListener('click', () => { dialog.showModal(); document.body.style.overflow = 'hidden'; }));
document.querySelector('.dialog-close').addEventListener('click', () => dialog.close());
dialog.addEventListener('click', e => { if (e.target === dialog) { const r=dialog.getBoundingClientRect(); if(e.clientX<r.left || e.clientX>r.right || e.clientY<r.top || e.clientY>r.bottom) dialog.close(); } });
dialog.addEventListener('close', () => { document.body.style.overflow = ''; });
const toggle = document.querySelector('.menu-toggle');
const menu = document.querySelector('.mobile-nav');
function closeMenu() { menu.hidden=true; toggle.setAttribute('aria-expanded','false'); toggle.setAttribute('aria-label','Открыть меню'); toggle.textContent='☰'; }
toggle.addEventListener('click', () => { const open=toggle.getAttribute('aria-expanded')==='true'; menu.hidden=open; toggle.setAttribute('aria-expanded',String(!open)); toggle.setAttribute('aria-label',open?'Открыть меню':'Закрыть меню'); toggle.textContent=open?'☰':'×'; });
menu.querySelectorAll('a').forEach(a=>a.addEventListener('click',closeMenu));
document.addEventListener('keydown',e=>{if(e.key==='Escape') closeMenu();});
document.getElementById('year').textContent = new Date().getFullYear();
if ('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  document.documentElement.classList.add('js-motion');
  const observer=new IntersectionObserver(entries=>{entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add('visible');observer.unobserve(entry.target);}});},{threshold:.08});
  document.querySelectorAll('.reveal').forEach(el=>observer.observe(el));
}
