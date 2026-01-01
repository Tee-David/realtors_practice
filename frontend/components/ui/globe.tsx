"use client";

import { useEffect, useRef, useState } from "react";

interface GlobeProps {
  className?: string;
}

export function Globe({ className }: GlobeProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    if (!canvasRef.current || typeof window === "undefined") return;

    let cleanup: (() => void) | null = null;

    // Dynamic import to avoid SSR issues
    Promise.all([
      import("three-globe"),
      import("three")
    ]).then(([{ default: createGlobe }, THREE]) => {
      const canvas = canvasRef.current;
      if (!canvas) return;

      const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
      renderer.setSize(canvas.offsetWidth, canvas.offsetHeight);
      renderer.setClearColor(0x000000, 0);

      const scene = new THREE.Scene();
      scene.fog = new THREE.Fog(0x000000, 400, 2000);

      const camera = new THREE.PerspectiveCamera(50, canvas.offsetWidth / canvas.offsetHeight, 0.1, 1000);
      camera.position.z = 300;

      const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
      scene.add(ambientLight);

      const directionalLight = new THREE.DirectionalLight(0xffffff, 0.6);
      directionalLight.position.set(0, 0, 1);
      scene.add(directionalLight);

      const Globe = createGlobe();
      Globe
        .globeImageUrl("//unpkg.com/three-globe/example/img/earth-blue-marble.jpg")
        .bumpImageUrl("//unpkg.com/three-globe/example/img/earth-topology.png")
        .backgroundImageUrl("//unpkg.com/three-globe/example/img/night-sky.png");

      Globe.rotation.y = -Math.PI * (5 / 9);
      Globe.rotation.z = -Math.PI / 6;

      const globeMaterial = Globe.globeMaterial() as any;
      globeMaterial.color = new THREE.Color(0x3a228a);
      globeMaterial.emissive = new THREE.Color(0x220038);
      globeMaterial.emissiveIntensity = 0.1;
      globeMaterial.shininess = 0.7;

      scene.add(Globe);

      let animationFrameId: number;

      const animate = () => {
        Globe.rotation.y += 0.001;
        renderer.render(scene, camera);
        animationFrameId = requestAnimationFrame(animate);
      };

      animate();
      setIsLoaded(true);

      const handleResize = () => {
        if (!canvasRef.current) return;
        const width = canvasRef.current.offsetWidth;
        const height = canvasRef.current.offsetHeight;
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
        renderer.setSize(width, height);
      };

      window.addEventListener("resize", handleResize);

      cleanup = () => {
        window.removeEventListener("resize", handleResize);
        cancelAnimationFrame(animationFrameId);
        renderer.dispose();
      };
    }).catch((error) => {
      console.error("Failed to load globe:", error);
    });

    return () => {
      if (cleanup) cleanup();
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className={className}
      style={{ width: "100%", height: "100%", display: "block" }}
    />
  );
}
