// Helper to get cookie
function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop()?.split(';').shift() || null;
  return null;
}

export type SSEEvent<T = any> = {
  type: string;
  data: T;
};

export class SSEConnection {
  private controller: AbortController | null = null;
  private url: string;
  private onMessage: (event: SSEEvent) => void;
  private onError: (error: any) => void;
  private method: string;
  private body: any;

  constructor(
    url: string, 
    onMessage: (event: SSEEvent) => void, 
    onError: (error: any) => void,
    method: string = 'GET',
    body: any = null
  ) {
    this.url = url;
    this.onMessage = onMessage;
    this.onError = onError;
    this.method = method;
    this.body = body;
  }

  async connect() {
    this.close();
    this.controller = new AbortController();
    
    const fullUrl = this.url.startsWith('http') 
        ? this.url 
        : `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}${this.url}`;

    try {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
      };
      
      const csrfToken = getCookie('csrf_token');
      if (csrfToken) {
        headers['X-CSRF-Token'] = csrfToken;
      }

      // We assume credentials are sent automatically (cookies) by browser for same-origin
      // For cross-origin with Fetch, we need credentials: 'include'
      
      const response = await fetch(fullUrl, {
        method: this.method,
        headers,
        body: this.body ? JSON.stringify(this.body) : undefined,
        signal: this.controller.signal,
        credentials: 'include', // Important for cookies
      });

      if (!response.ok) {
        throw new Error(`SSE error: ${response.status}`);
      }

      if (!response.body) {
        throw new Error('No response body');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        
        // Parse SSE format
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || ''; // Keep incomplete part
        
        for (const line of lines) {
           const eventMatch = line.match(/event: (.+)\n/);
           const dataMatch = line.match(/data: (.+)/);
           
           if (eventMatch && dataMatch) {
             const eventType = eventMatch[1];
             const rawData = dataMatch[1];
             try {
                const data = JSON.parse(rawData);
                this.onMessage({ type: eventType, data });
             } catch (e) {
                 console.error('JSON parse error', e);
             }
           }
        }
      }
    } catch (err: any) {
        if (err.name !== 'AbortError') {
            this.onError(err);
        }
    }
  }

  close() {
    if (this.controller) {
      this.controller.abort();
      this.controller = null;
    }
  }
}

