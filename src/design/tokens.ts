export const color = {
  ink: '#1E1B3A', ink2: '#3A3654', inkMuted: '#5E5A72', onInk: '#FFFFFF',
  sheet: '#FFFDF8', surface: '#FFFFFF', coral: '#FF6F59', violet: '#6A3FD1',
  success: '#137A4B', successBg: '#D4F5E3', mintSoft: '#DDF5EC',
  lavender: '#A99BFF', lemon: '#FFD84D', mint: '#6FD6AE',
  line: 'rgba(30,27,58,.16)', lineSoft: 'rgba(30,27,58,.12)',
  ledge: 'rgba(30,27,58,.14)', ledgeStrong: 'rgba(30,27,58,.3)',
  ledgeTile: 'rgba(30,27,58,.25)', track: 'rgba(30,27,58,.12)',
} as const;
export const layout = {width: 360, height: 640, scale: 3, left: 20, safeWidth: 280} as const;
export const radius = {pill: 999, chip: 14, option: 20, card: 22, sheet: 40} as const;
export const border = {normal: 2, blank: 3} as const;
export const ledge = (height = 4, tint: string = color.ledge) => `0 ${height}px 0 ${tint}`;
