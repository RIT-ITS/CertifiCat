interface RGB {
    r: number,
    g: number,
    b: number
}

export function blendColors(color1: string, color2: string, ratio: number) {
    // Ensure ratio is between 0 and 1
    ratio = Math.max(Math.min(ratio, 1), 0);

    // Convert hex colors to RGB
    const rgb1 = hexToRgb(color1);
    const rgb2 = hexToRgb(color2);

    // Blend RGB colors
    const blendedRgb = {
        r: Math.round(rgb1.r * (1 - ratio) + rgb2.r * ratio),
        g: Math.round(rgb1.g * (1 - ratio) + rgb2.g * ratio),
        b: Math.round(rgb1.b * (1 - ratio) + rgb2.b * ratio)
    };

    // Convert blended RGB back to hex
    return rgbToHex(blendedRgb);
}

export function hexToRgb(hex: string): RGB {
    // Remove # if present
    hex = hex.replace("#", "");

    // Convert hex values to decimal
    const r = parseInt(hex.substring(0, 2), 16);
    const g = parseInt(hex.substring(2, 4), 16);
    const b = parseInt(hex.substring(4, 6), 16);

    return { r, g, b };
}

export function rgbToHex(rgb: RGB) {
    // Convert decimal values to hex and pad with zeros if necessary
    const rHex = rgb.r.toString(16).padStart(2, "0");
    const gHex = rgb.g.toString(16).padStart(2, "0");
    const bHex = rgb.b.toString(16).padStart(2, "0");

    // Concatenate hex values and add # prefix
    return "#" + rHex + gHex + bHex;
}