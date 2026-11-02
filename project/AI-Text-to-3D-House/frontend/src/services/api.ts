export const API_BASE_URL = 'http://localhost:8000';

function getHeaders() {
    const token = localStorage.getItem('ai_house_token');
    return {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    };
}

export async function registerUser(email: string, password: string) {
    const res = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
        const text = await res.text();
        throw new Error(`Registration failed: ${res.status} ${text}`);
    }
    return res.json();
}

export async function loginUser(email: string, password: string) {
    const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
        const text = await res.text();
        throw new Error(`Login failed: ${res.status} ${text}`);
    }
    return res.json();
}

export async function getMe() {
    const res = await fetch(`${API_BASE_URL}/api/auth/me`, {
        headers: getHeaders()
    });
    if (!res.ok) {
        throw new Error('Not authenticated');
    }
    return res.json();
}

export async function generateHouse(prompt: string) {
    const res = await fetch(`${API_BASE_URL}/api/generate`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ prompt }),
    });

    if (!res.ok) {
        const text = await res.text();
        throw new Error(`Generation failed: ${res.status} ${text}`);
    }

    return await res.json();
}

// Designs CRUD

export async function getDesigns() {
    const res = await fetch(`${API_BASE_URL}/api/designs`, {
        headers: getHeaders()
    });
    if (!res.ok) {
        throw new Error('Failed to fetch designs');
    }
    return res.json();
}

export async function saveDesign(designData: any) {
    const res = await fetch(`${API_BASE_URL}/api/designs`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(designData),
    });
    if (!res.ok) {
        const text = await res.text();
        throw new Error(`Failed to save design: ${res.status} ${text}`);
    }
    return res.json();
}

export async function updateDesign(id: string, designData: any) {
    const res = await fetch(`${API_BASE_URL}/api/designs/${id}`, {
        method: 'PUT',
        headers: getHeaders(),
        body: JSON.stringify(designData),
    });
    if (!res.ok) {
        const text = await res.text();
        throw new Error(`Failed to update design: ${res.status} ${text}`);
    }
    return res.json();
}

export async function deleteDesign(id: string) {
    const res = await fetch(`${API_BASE_URL}/api/designs/${id}`, {
        method: 'DELETE',
        headers: getHeaders(),
    });
    if (!res.ok) {
        const text = await res.text();
        throw new Error(`Failed to delete design: ${res.status} ${text}`);
    }
    // 204 No Content returns no JSON
    return true;
}
