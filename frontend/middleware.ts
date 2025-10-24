import { NextRequest, NextResponse } from 'next/server'

export function middleware(request: NextRequest) {
  const authToken = request.cookies.get('auth_token')?.value
  const { pathname } = request.nextUrl

  // Public routes that don't require authentication
  const publicRoutes = ['/auth/login', '/auth/callback', '/', '/pricing', '/features']

  // Check if the route is public
  const isPublicRoute = publicRoutes.some(route => 
    pathname === route || pathname.startsWith(route + '/')
  )

  // If accessing protected route without token, redirect to login
  if (!isPublicRoute && !authToken) {
    return NextResponse.redirect(new URL('/auth/login', request.url))
  }

  // If accessing login page with valid token, redirect to dashboard
  if (pathname === '/auth/login' && authToken) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)']
}
