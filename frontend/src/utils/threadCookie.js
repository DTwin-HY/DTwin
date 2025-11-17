const THREAD_COOKIE_NAME = 'dtwin_thread_ids';
const MAX_AGE_SECONDS = 12 * 60 * 60; // 12h

const safeParse = (value) => {
  try {
    return value ? JSON.parse(value) : {};
  } catch {
    return {};
  }
};

const getCookieRaw = () => {
  if (typeof document === 'undefined') return null;
  const match = document.cookie.match(new RegExp('(^| )' + THREAD_COOKIE_NAME + '=([^;]+)'));
  return match ? decodeURIComponent(match[2]) : null;
};

const setCookieRaw = (valueObj) => {
  if (typeof document === 'undefined') return;
  const encoded = encodeURIComponent(JSON.stringify(valueObj));
  document.cookie = `${THREAD_COOKIE_NAME}=${encoded}; max-age=${MAX_AGE_SECONDS}; path=/`;
};

export const getThreadIdForUser = (userId) => {
  const raw = getCookieRaw();
  const map = safeParse(raw);
  return map?.[String(userId)] || null;
};

export const setThreadIdForUser = (userId, threadId) => {
  const raw = getCookieRaw();
  const map = safeParse(raw);
  map[String(userId)] = threadId;
  setCookieRaw(map);
};

export const clearThreadIdForUser = (userId) => {
  const raw = getCookieRaw();
  const map = safeParse(raw);
  delete map[String(userId)];
  setCookieRaw(map);
};
