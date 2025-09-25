import '@testing-library/jest-dom'

if (!window.matchMedia) {
  window.matchMedia = (query: string): MediaQueryList => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  })
}

class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}

if (!('ResizeObserver' in window)) {
  // @ts-expect-error jsdom global augmentation
  window.ResizeObserver = ResizeObserverMock
  // @ts-expect-error jsdom global augmentation
  global.ResizeObserver = ResizeObserverMock
}
