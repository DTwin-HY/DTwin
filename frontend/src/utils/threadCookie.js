const THREAD_COOKIE_NAME = 'dtwin_thread_id';

export const getThreadCookie = () => {
  if (typeof document === 'undefined') return null;
  const match = document.cookie.match(
    new RegExp('(^| )' + THREAD_COOKIE_NAME + '=([^;]+)')
  );
  return match ? match[2] : null;
};

export const setThreadCookie = (id) => {
  if (typeof document === 'undefined') return;
  const maxAgeSeconds = 12 * 60 * 60; // 12h
  document.cookie = `${THREAD_COOKIE_NAME}=${id}; max-age=${maxAgeSeconds}; path=/`;
};

export const clearThreadCookie = () => {
  if (typeof document === 'undefined') return;
  document.cookie = `${THREAD_COOKIE_NAME}=; Max-Age=0; path=/`;
};
