import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

let scene, camera, renderer, controls;

export function initScene() { //Для дефолтного отображения на сайте

    scene = new THREE.Scene(); //Сцена
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000); //Камера
    renderer = new THREE.WebGLRenderer(); //Рендерер

    renderer.setClearColor(20 / 255, 20 / 255, 20 / 255);  //Поменять цвет
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    orbControls();
    axes();
    initPlane();
    initGrid();

    camera.position.set(5, 5, 10)
    animate();

};

function orbControls() {

    controls = new OrbitControls(camera, renderer.domElement); //Вращение камеры
    controls.enableDamping = true;
    controls.dampingFactor = 0.05; //Еффект перемещения
    controls.screenSpacePanning = false;
    controls.minDistance = 2;
    controls.maxDistance = 20;

};

function axes() {

    const axes = [
        {dir: new THREE.Vector3(5, 0, 0), hex: 0xff0000}, //X axis
        {dir: new THREE.Vector3(0, 5, 0), hex: 0x00ff00}, //Y axis
        {dir: new THREE.Vector3(0, 0, 5), hex: 0x0000ff}, //Z axis
    ];
    axes.forEach((axis) => {
        axis.dir.normalize();
        const length = 2;
        const origin = new THREE.Vector3(0, 0, 0);

        const arrowHelper = new THREE.ArrowHelper(axis.dir, origin, length, axis.hex);
        scene.add(arrowHelper);
    });

};

function initPlane() {

    const plane_geom = new THREE.PlaneGeometry(15, 15); //Плоскость XOY
    const material_for_plane = new THREE.MeshBasicMaterial({
        color: 0xf7fb99, 
        side: THREE.DoubleSide, 
        transparent: true,
        opacity: 0.7,  //Прозрачность
        visible: false,
    });
    const plane = new THREE.Mesh(plane_geom, material_for_plane);
    scene.add(plane);

};

function initGrid() {

    const grid = new THREE.GridHelper(15, 15);      //Сетка
    grid.rotation.x = Math.PI / 2;      //ХОY
    scene.add(grid);

};

export function threeScene(points) {

    console.log("Received coordinates: ", points);
    console.log(typeof points);

    const line_material = new THREE.LineBasicMaterial({color: 'blue'});

    animate();

}

function animate() {

    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);

}

