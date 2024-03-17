function switchLanguage(lang) {
  const body = document.querySelector('body');
  body.classList.remove('lang-fr', 'lang-en');
  body.classList.add('lang-' + lang);
}

