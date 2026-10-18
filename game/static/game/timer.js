/* Display only: the server is authoritative for every game deadline. */
document.querySelectorAll('[data-expires]').forEach((element) => {
  const deadline = Date.parse(element.dataset.expires);
  function update() {
    const seconds = Math.max(0, Math.ceil((deadline - Date.now()) / 1000));
    element.textContent = `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`;
    if (seconds === 0) element.textContent = 'Time reached — refresh to check';
  }
  update();
  window.setInterval(update, 1000);
});
