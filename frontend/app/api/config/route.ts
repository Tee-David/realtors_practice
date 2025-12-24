import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    apiUrl: process.env.NEXT_PUBLIC_API_URL || 'https://realtors-practice-api.onrender.com/api',
    nodeEnv: process.env.NODE_ENV,
    envFileDetected: !!process.env.NEXT_PUBLIC_API_URL,
  });
}
