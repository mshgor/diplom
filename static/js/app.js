import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { MeshLine, MeshLineMaterial } from 'three.meshline';
import {pass} from 'three/tsl';

let scene, camera, renderer, controls;

export function initScene() {
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    renderer = new THREE.WebGLRenderer();

    renderer.setClearColor(20 / 255, 20 / 255, 20 / 255);
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    camera.up.set(0, 0, 1);
    camera.position.set(-20, -20, 40);
    camera.updateProjectionMatrix();
    camera.updateMatrixWorld();

    orbControls();
    axes();
    initPlane();
    initGrid();
    animate();
};

function orbControls() {
    controls = new OrbitControls(camera, renderer.domElement);
    controls.mouseButtons.LEFT = THREE.MOUSE.PAN;
    controls.mouseButtons.RIGHT = THREE.MOUSE.ROTATE;
    controls.keys = {
        LEFT: 'ArrowLeft',
        RIGHT: 'ArrowRight',
        UP: 'ArrowUp',
        BOTTOM: 'ArrowDown' 
    }
    controls.listenToKeyEvents(window);
};

function axes() {
    const axes = [
        {dir: new THREE.Vector3(50, 0, 0), hex: 0xff0000},
        {dir: new THREE.Vector3(0, 50, 0), hex: 0x00ff00},
        {dir: new THREE.Vector3(0, 0, 50), hex: 0x0000ff},
    ];
    axes.forEach((axis) => {
        const arrowHelper = new THREE.ArrowHelper(axis.dir, new THREE.Vector3(0, 0, 0), 15, axis.hex);
        scene.add(arrowHelper);
    });
};

function initPlane() {
    const plane = new THREE.Mesh(
        new THREE.PlaneGeometry(50, 50),
        new THREE.MeshBasicMaterial({ 
            color: 0xf7fb99,
            side: THREE.DoubleSide,
            transparent: true,
            opacity: 0.7,
            visible: false
        })
    );
    scene.add(plane);
};

function initGrid() {
    const grid = new THREE.GridHelper(50, 50);
    grid.rotateX(Math.PI / 2);
    scene.add(grid);
};

export function threeScene(points) {
    // Очистка предыдущих линий
    [...scene.children].forEach(child => {
        if (child.isMesh && child.material instanceof MeshLineMaterial) {
            child.geometry.dispose();
            child.material.dispose();
            scene.remove(child);
        }
    });

    // Материалы
    const material_G0 = new MeshLineMaterial({ 
        color: 0xffd500,
        lineWidth: 0.03,
        dashArray: 0.1,
        dashRatio: 0.5
    });

    const material_cut = new MeshLineMaterial({
        color: 0x00e4ff,
        lineWidth: 0.05
    });
    
    let received_points = points.result;
    console.log(received_points);
    let current_point, previous_point;

    for (let i = 0; i < received_points.length; i++) {
        
        let is_arc, clockwise = true;
        let x, y, z, f, r, start_angle, end_angle, material_line;
        let center = [];
        let g = [];
        console.log(received_points[i]);
        let dict = received_points[i];

        for (let key in dict) {
           
            switch (key) {

                case "G": g = dict.G; break;
                case "X": x = dict.X; break;
                case "Y": y = dict.Y; break;
                case "Z": z = dict.Z; break;
                case "F": f = dict.F; break;
                case "Center": center = dict.Center; break;
                case "R": r = dict.R; break;
                case "StartAngle": start_angle = dict.StartAngle; break;
                case "EndAngle": end_angle = dict.EndAngle; break;
            };

        }

        x = (typeof x !== 'undefined') ? x : (previous_point?.x ?? 0);
        y = (typeof y !== 'undefined') ? y : (previous_point?.y ?? 0);
        z = (typeof z !== 'undefined') ? z : (previous_point?.z ?? 0);

        is_arc = (g.includes(2) || g.includes(3)) ? true : false;
        clockwise = (g.includes(3)) ? false : true;  
        material_line = (g.includes(0)) ? material_G0 : material_cut;
        
        if (!is_arc) {
            
            current_point = new THREE.Vector3(x, y, z);
            if (i === 0) {
                previous_point = current_point;
                continue;
            }

            let points = [
                previous_point.x || 0, previous_point.y || 0, previous_point.z || 0,
                current_point.x || 0, current_point.y || 0, current_point.z || 0
            ];

            const line_geometry = new THREE.BufferGeometry();
            line_geometry.setAttribute('position', new THREE.Float32BufferAttribute(points, 3));

            const line = new MeshLine();
            line.setGeometry(line_geometry);

            let mesh = new THREE.Mesh(line.geometry, material_line);
            scene.add(mesh);

            previous_point = current_point;
        }

        else {

            const curve = new THREE.ArcCurve(
                center[0], 
                center[1],
                r,
                start_angle,
                end_angle,
                clockwise
            );
            const points = curve.getPoints(50);
            const positions = new Float32Array(points.length * 3);
            points.forEach((p, i) => {
                positions[i * 3] = p.x;
                positions[i * 3 + 1] = p.y;
                positions[i * 3 + 2] = z;
            });

            const geometry = new THREE.BufferGeometry();
            geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

            const line = new MeshLine();
            line.setGeometry(geometry);

            scene.add(new THREE.Mesh(line.geometry, material_line));
            previous_point = new THREE.Vector3(x, y, z);

        }
    }

};

function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
};
