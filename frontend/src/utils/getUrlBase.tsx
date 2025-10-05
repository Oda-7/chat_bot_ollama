const getUrlBase = () => {
  const winEnv = (typeof window !== 'undefined' && (window as any).__ENV) || {};
  let wsBase = (
    winEnv.REACT_APP_API_BASE_URL || 'http://localhost:8000'
  ).trim();

  return wsBase;
};

export default getUrlBase;
