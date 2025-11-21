var babylonScene = null;
var babylonEngine = null;

function createLabel(text, parentMesh) {
    if (!babylonScene) return;

    const roomName = parentMesh.name.replace("anchor_", "");

    const labelPlane = BABYLON.MeshBuilder.CreatePlane(roomName, {
        size: 3,
        sideOrientation: BABYLON.Mesh.DOUBLESIDE
    }, babylonScene);

    labelPlane.parent = parentMesh;
    labelPlane.position = BABYLON.Vector3.Zero();
    labelPlane.rotation.y = Math.PI;
    labelPlane.rotation.z = Math.PI;

    labelPlane.billboardMode = BABYLON.AbstractMesh.BILLBOARDMODE_ALL;

    const labelTexture = BABYLON.GUI.AdvancedDynamicTexture.CreateForMesh(
        labelPlane, 1024, 1024, false, true
    );

    const textBlock = new BABYLON.GUI.TextBlock(`text_for_${roomName}`);
    textBlock.text = text;
    textBlock.color = "black";
    textBlock.fontSize = 80;
    textBlock.outlineWidth = 0;

    labelTexture.addControl(textBlock);

    labelPlane.textBlock = textBlock;
    labelPlane.isPickable = false;
}

window.updateLabel = function (roomName, newText) {
    if (!babylonScene) return;

    const labelPlane = babylonScene.getMeshByName(roomName);

    if (labelPlane && labelPlane.textBlock) {
        labelPlane.textBlock.text = newText;
    } else {
        console.log(`${roomName} room not found.`);
    }
}

async function loadBabylonScene() {
    if (typeof BABYLON === 'undefined' ||
        typeof BABYLON.GUI === 'undefined' ||
        typeof BABYLON.SceneLoader === 'undefined') {
        console.log("Waiting for scripts to load.");
        setTimeout(loadBabylonScene, 100);
        return;
    }

    await actualLoadBabylonScene();
}

async function actualLoadBabylonScene() {
    const canvas = document.getElementById("renderCanvas");
    babylonEngine = new BABYLON.Engine(canvas, true);
    babylonScene = new BABYLON.Scene(babylonEngine);

    const camera = new BABYLON.ArcRotateCamera("Camera", 3 * Math.PI / 4, Math.PI / 4, 25, BABYLON.Vector3.Zero(), babylonScene);
    camera.attachControl(canvas, false);
    camera.lowerRadiusLimit = 5;
    camera.upperRadiusLimit = 30;
    camera.upperBetaLimit = Math.PI / 2;
    const light = new BABYLON.HemisphericLight("light", new BABYLON.Vector3(0, 1, 0), babylonScene);
    babylonScene.clearColor = new BABYLON.Color4(0, 0, 0, 0);

    await BABYLON.SceneLoader.AppendAsync("/models/", "model.glb", babylonScene);

    const roomLabelAnchors = ["anchor_external", "anchor_boiler", "anchor_garage", "anchor_bedroom1", "anchor_bedroom2", "anchor_bathroom", "anchor_living_room"];

    roomLabelAnchors.forEach(anchorName => {
        const mesh = babylonScene.getTransformNodeByName(anchorName);
        if (mesh) {
            createLabel(anchorName, mesh);
        } else {
            console.log(`${anchorName} etiquette not found.`);
        }
    });

    const interactiveObjects = ["battery", "heat_pump_inside", "heat_pump_outside", "pv", "ventilation", "wallbox", "water_heater"];
    interactiveObjects.forEach(name => {
        const mesh = babylonScene.getMeshByName(name);
        if (mesh) {
            mesh.isPickable = true;
        }
    });

    babylonEngine.runRenderLoop(() => {
        babylonScene.render();
    });

    window.addEventListener("resize", () => {
        babylonEngine.resize();
    });
}