import type { NextConfig } from 'next';
const config: NextConfig = {
  // The hosted demo serves this static Next.js build from FastAPI on one origin.
  ...(process.env.FINN_STATIC_EXPORT === '1' ? { output: 'export' as const } : {}),
};
export default config;
