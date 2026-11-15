import './globals.css';
import type { Metadata } from 'next';
export const metadata: Metadata={title:'FINN · Investment intelligence',description:'Portfolio signals, primary-source research and professional context.'};
export default function Layout({children}:{children:React.ReactNode}){return <html lang="en"><body>{children}</body></html>}
