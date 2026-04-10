export function getErrorMessage(error: unknown) {
	if (error instanceof Error) return error.message
	return String(error)
}

export function getCookie(name: string): string | undefined {
	const value = `; ${document.cookie}`;
	const parts = value.split(`; ${name}=`);
	if (parts.length === 2) return parts.pop()?.split(';').shift();

	return undefined;
}

export const getCsrfToken = () => getCookie('csrftoken');