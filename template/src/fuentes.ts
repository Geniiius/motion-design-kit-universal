import { loadFont } from "@remotion/fonts";
import inter400 from "@fontsource/inter/files/inter-latin-400-normal.woff2";
import inter600 from "@fontsource/inter/files/inter-latin-600-normal.woff2";
import grotesk500 from "@fontsource/space-grotesk/files/space-grotesk-latin-500-normal.woff2";
import grotesk700 from "@fontsource/space-grotesk/files/space-grotesk-latin-700-normal.woff2";

// Fuentes locales (licencia OFL): el render no necesita conexión a internet.
export const fuentes = { display: "Space Grotesk", body: "Inter" } as const;

loadFont({ family: fuentes.body, url: inter400, weight: "400" });
loadFont({ family: fuentes.body, url: inter600, weight: "600" });
loadFont({ family: fuentes.display, url: grotesk500, weight: "500" });
loadFont({ family: fuentes.display, url: grotesk700, weight: "700" });
