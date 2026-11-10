import { Config } from "@remotion/cli/config";

// Salida compatible con todas las redes sociales (H.264 + yuv420p)
Config.setVideoImageFormat("jpeg");
Config.setCodec("h264");
Config.setPixelFormat("yuv420p");
Config.setCrf(18);
Config.setOverwriteOutput(true);
// WebGL por GPU (ANGLE): necesario para las escenas 3D con @remotion/three
Config.setChromiumOpenGlRenderer("angle");
