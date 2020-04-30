const params = {
    gravity : 5,
    wind : () => (0 + Math.random()-.5),
    windDir : () => Math.random() < 0.5 ? -1 : 1,
    scale : 5,
    landSite : 0,                               // 0 = left, 1 = center, 2 = right
    startSite : 2,                              // 0 = left, 1 = center, 2 = right
    platformType : 1,                           // -1 = pit, 0 = flat, 1 = hill
    timeToWin: 5,
    lander : {
        startRandom : true,
        w : 10+(15-2)+25,                         // top vert + dome radius + foot offset
        h : 15*2,
        thrust : 10,
        turning : 1.0,
        hullVerts : {
            top : {x:15, y:-10},
            mid : {x:15, y:0  },
            bot : {x:5,  y:10 }
        },
        footOff : {x:20, y:25},
        footW : 8,
        footH : 2,
        footDensity : 0.005,
        springFreq : 8,
        springDamp : 6
    },
    floor : {
        chunks : 33,
        height : 100,
        hillHeight: 50,
        fluctSize : .5,                         // Height fluctuation size of ground chunks (as fraction of hill height)
        friction : 0.8,
        restitution : 0.0,
    },
    colors : {
        sky : '#2f3e59',
        lander : '#f07a56',
        feet : '#f07a56',
        legs : '#ffffff',
        dome : '#8acede',
        floor : '#bdb69b',
        platform : '#ffffff',
        pauseBackground: '#2f3e59',
        pauseText: '#f07a56'
    },
    hyper : {
        logData : false,
        debug : false,
        timeLimit : 300,                          // in seconds (0 to remove time limit)
        seed: false,
        updatePeriod : 1/80,                     // simulation step size (seconds)
        positionIterations : 3,
        velocityIterations : 8
    }
};

const scaled = (x) => {return x/params.scale};
const unscaled = (x) => {return x*params.scale};
const toDegrees = (angle_rad) => {return Math.abs((angle_rad/Math.PI*180) % 360)};
const toRadians = (angle_deg) => {return Math.PI*angle_deg/180};
const getEuclidDistance = (u, w) => {return Math.sqrt((u[0]-w[0])**2+(u[1]-w[1])**2)};
const inSec = (ms) => {return ms/1000};
const rotate = (x, y, t) => {return [x*Math.cos(t)-y*Math.sin(t), x*Math.sin(t)+y*Math.cos(t)]};

function runGame() {
    const canvas = document.getElementById('mainCanvas');
    const context = canvas.getContext('2d');
    const stage = new createjs.Stage(canvas);
    const debugCanvas = document.getElementById('debugCanvas');
    const debugContext = debugCanvas.getContext('2d');
    const debugStage = new createjs.Stage(debugCanvas);
    const floorChunkBodies = new Array();
    const chunkWidth = canvas.width / params.floor.chunks
    let world;
    let wind = params.wind() * params.windDir();

    let floorView = new createjs.Shape();
    let platformView = new createjs.Shape();
    let flagPost;
    let landerBody;
    let feetBodies;
    let hullView;
    let domeView;
    let footViews;
    let legViews;

    let lastUpdateTime;
    let trialStartTime;
    let accumulator = 0;
    let gamePaused = true;
    let pauseMessage = new createjs.Text('Press \'SPACE\' to continue', '40px Arial', params.colors.pauseText);
    pauseMessage.x = canvas.width/2;
    pauseMessage.y = canvas.height/2;
    pauseMessage.textAlign = 'center';
    pauseMessage.textBaseline = 'middle';
    let pauseBackground = new createjs.Shape;
    pauseBackground.graphics.beginFill(params.colors.pauseBackground).drawRect(0, 0, canvas.width, canvas.height);

    let landPoint;
    let sensPoint;
    let distToLandPoint = NaN;
    let enterTime = false;
    let sinceEnter = 0;
    let fuel = 0;

    let crash = false;
    let landed = false;
    let userReset = false;

    let collisionListener = new Box2D.Dynamics.b2ContactListener;
    collisionListener.BeginContact = onBeginContact;

    document.addEventListener('visibilitychange', reportVisibilityChange);

    const background = new createjs.Shape;
    background.graphics.beginFill(params.colors.sky).drawRect(0, 0, canvas.width, canvas.height);
    stage.addChild(background);

    if (params.hyper.seed) {Math.seedrandom('lunar-lander-random-seed')};
    init();

    // Run initializers
    function init() {
        world = new Box2D.Dynamics.b2World(
            new Box2D.Common.Math.b2Vec2(wind, params.gravity), true);

        world.SetContactListener(collisionListener);
        initFloor();
        initLander();
        if (params.hyper.debug) {
            initBox2DDebug();
        }
        initKeyboard();
        trialStartTime = new Date().getTime();
        createjs.Ticker.addEventListener('tick', draw);
        createjs.Ticker.useRAF = true;
        pauseUnpause(gamePaused);
        tick();
    };

    //Initialize Box2D debug
    function initBox2DDebug() {
        var debugDraw = new Box2D.Dynamics.b2DebugDraw();
        debugDraw.SetSprite(debugContext);
        debugDraw.SetDrawScale(params.scale);
        debugDraw.SetFillAlpha(.1);
        debugDraw.SetLineThickness(1);
        debugDraw.SetFlags(Box2D.Dynamics.b2DebugDraw.e_shapeBit | Box2D.Dynamics.b2DebugDraw.e_jointBit);
        world.SetDebugDraw(debugDraw);
    };

    //Initializes keyboard events
    function initKeyboard() {
        document.addEventListener('keydown', function (event) {
            if (38 == event.keyCode) {
                landerBody.GetUserData().thrusting = true;
            } else if (37 == event.keyCode) {
                landerBody.GetUserData().turningLeft = true;
            } else if (39 == event.keyCode) {
                landerBody.GetUserData().turningRight = true;
            } else if (32 == event.keyCode) {
                gamePaused = !gamePaused
            } else if (68 == event.keyCode) {
                params.hyper.debug = !params.hyper.debug
            } else if (82 == event.keyCode) {
                userReset = !userReset
            }
        });

        document.addEventListener('keyup', function (event) {
            if (38 == event.keyCode) {
                landerBody.GetUserData().thrusting = false;
            } else if (37 == event.keyCode) {
                landerBody.GetUserData().turningLeft = false;
            } else if (39 == event.keyCode) {
                landerBody.GetUserData().turningRight = false;
            }
        });
    };

    // Initialize the lander
    function initLander() {
        let landerData = {
            'kind' : 'lander',
            'width' : params.lander.w,
            'height' : params.lander.h,
            'thrusting' : false,
            'turningLeft' : false,
            'turningRight' : false,
            'thrust' : params.lander.thrust,
            'turning' : params.lander.turning,
        };
        site = (canvas.width/3)*params.startSite
        const xPos = params.lander.startRandom ? site+canvas.width/3*Math.random() : site+canvas.width/3/2;
        const yPos = 40;

        parts = getLanderParts(xPos, yPos, 1, 0.8, 0.0, world);

        landerBody = parts.bodies.lander;
        landerBody.SetUserData(landerData);
        feetBodies = parts.bodies.feet;
        sensorBody = parts.bodies.sensor;

        Object.values(parts.views).forEach(viewArr => viewArr.forEach(view => stage.addChild(view)));
        domeView = parts.views.lander[0];
        hullView = parts.views.lander[1];
        footViews = parts.views.feet;
        legViews = parts.views.legs;
    };

    // Initialize terrain
    function initFloor() {
        const depth = canvas.height - params.floor.height
        const flucts = new Array();
        start = 2*Math.PI*Math.random();
        stop = start + 2*Math.PI;
        step = (stop-start)/params.floor.chunks;
        for(let j = start; j <= stop+1; j += step) {
            wave = params.floor.hillHeight*Math.sin(j);
            noise = Math.random()*params.floor.hillHeight*params.floor.fluctSize;
            flucts.push(params.floor.height+wave+noise);
        };

        const centroid = Math.floor(params.floor.chunks/3/2) + Math.floor(params.floor.chunks/3)*params.landSite
        flucts[centroid] +=  params.floor.height*params.platformType
        flucts[centroid-1] = flucts[centroid];
        flucts[centroid+1] = flucts[centroid];
        flucts[centroid+2] = flucts[centroid];

        floorView.graphics.beginFill(params.colors.floor);
        floorView.graphics.moveTo(0, depth - flucts[0])

        for (let i=0; i<params.floor.chunks; i++) {
            floorChunkBodies.push(addChunk(
                xPos   = chunkWidth/2 + i*chunkWidth,
                yPos   = canvas.height - params.floor.height/2,
                width  = chunkWidth,
                height = params.floor.height,
                left   = flucts[i],
                right  = flucts[i+1],
                world  = world,
                stg    = stage
            ));
            floorView.graphics.lineTo((i+1)*chunkWidth, depth - flucts[i+1]);
        };
        floorView.graphics.lineTo(canvas.width, canvas.height).lineTo(0, canvas.height)
        stage.addChild(floorView)

        platformView.graphics.beginFill(params.colors.platform).drawRect(
            chunkWidth*centroid-chunkWidth, depth - flucts[centroid+1],
            chunkWidth*3, 10
        );
        stage.addChild(platformView);
        landPoint = [chunkWidth*centroid+chunkWidth/2, depth-flucts[centroid+1]-params.lander.h/2];
        sensPoint = [chunkWidth*centroid+chunkWidth/2, depth-flucts[centroid+1]+10];
    };

    // Init flag
    function addFlag(x, y) {
    //    const bitmap = new createjs.Bitmap("imagePath.jpg");
        const h = 60;
        flagPost = new createjs.Shape;
        flagPost.graphics.beginFill('white').drawRect(x, y-h, 2, h);
        flagPost.graphics.beginFill('white').drawRect(x+2, y-h, 30, 20);
        stage.addChild(flagPost);
    };

    // Reset episode
    function endTrial() {
        // Destroy world (by creating a new one)
        wind = params.wind() * params.windDir();
        world = new Box2D.Dynamics.b2World(
            new Box2D.Common.Math.b2Vec2(wind, params.gravity), true);
        world.SetContactListener(collisionListener);

        // Remove graphics
        hullView.graphics.clear();
        domeView.graphics.clear();
        floorView.graphics.clear();
        platformView.graphics.clear();
        footViews.forEach(view => view.graphics.clear());
        legViews.forEach(view => view.graphics.clear());
        trialStartTime = new Date().getTime();

        // Reset ticker and reinitialize world objects
        createjs.Ticker.reset();
        createjs.Ticker.init();
        createjs.Ticker.addEventListener('tick', simulate);
        createjs.Ticker.useRAF = true;
        initFloor();
        initLander();
        enterTime = false;
        landed = false;
        gamePaused = true;
        pauseUnpause(gamePaused); // Add pause graphics after other objects to draw it first
        userReset = false;
        fuel = 0;
        // $.ajax({})
    };

    // Simulate physics for time period `dt`
    function simulate(dt) {
        let impulse;
        let steeringPoint;
        let shipData = landerBody.GetUserData();
        let landerXpx = unscaled(landerBody.GetPosition().x)
        let landerYpx = unscaled(landerBody.GetPosition().y)
        let sX = unscaled(sensorBody.GetPosition().x)
        let sY = unscaled(sensorBody.GetPosition().y)

        var stopFlags = [
            landerXpx < -20,
            landerXpx > canvas.width+20,
            landerYpx < -20,
            sinceEnter >= params.timeToWin,
            userReset,
            params.hyper.timeLimit && (inSec(createjs.Ticker.getTime(true)) > params.hyper.timeLimit),
        ];
        if (stopFlags.some((flag) => flag)) {endTrial()};

        if (landerInBox(landerXpx, landerYpx, landPoint)) {
            world.m_gravity.x = 0
        } else {
            world.m_gravity.x = wind;
        };
        landed = sensorInBox(sX, sY, sensPoint);
        if (landed) {
            if (!enterTime) {
              enterTime = createjs.Ticker.getTime(true);
            } else {
              sinceEnter = inSec(createjs.Ticker.getTime(true) - enterTime);
            };
        } else {
            enterTime = false;
            sinceEnter = 0;
        };

        if (shipData.thrusting) {
            impulse = new Box2D.Common.Math.b2Vec2(Math.sin(landerBody.GetAngle()) * shipData.thrust,
                -(Math.cos(landerBody.GetAngle()) * shipData.thrust));
            landerBody.ApplyImpulse(impulse, landerBody.GetWorldCenter());
            fuel += 1;
        }

        if (shipData.turningLeft || shipData.turningRight) {
            steeringPoint = landerBody.GetWorldCenter().Copy();
            steeringPoint.y -= (shipData.height / 2 + 1) / params.scale;
            fuel += 1;
        }
        if (shipData.turningLeft) {
            impulse = new Box2D.Common.Math.b2Vec2(-shipData.turning, 0);
            landerBody.ApplyImpulse(impulse, steeringPoint);
        }
        if (shipData.turningRight) {
            impulse = new Box2D.Common.Math.b2Vec2(shipData.turning, 0);
            landerBody.ApplyImpulse(impulse, steeringPoint);
        }
        distToLandPoint = getEuclidDistance(
            u = landPoint,
            w = [landerXpx, landerYpx]);

        world.Step(dt, params.hyper.velocityIterations, params.hyper.positionIterations);
    };

    // Time-update function to handle variable frame rate
    function update(dt) {
        if (gamePaused || reportVisibilityChange()) {
            pauseUnpause(gamePaused)
        } else {
            pauseUnpause(gamePaused)
            accumulator += (dt)
            while (accumulator > params.hyper.updatePeriod) {
                simulate(params.hyper.updatePeriod);
                accumulator -= params.hyper.updatePeriod;
            }
        }
    };

    //Draw world and log game state
    function draw() {
        if (params.hyper.debug) {
            world.DrawDebugData();
        } else {
            debugContext.clearRect(0, 0, debugCanvas.width, debugCanvas.height)
        }

        const lX = unscaled(landerBody.GetPosition().x);
        const lY = unscaled(landerBody.GetPosition().y);

        for (let view of [hullView, domeView]) {
            view.x = lX;
            view.y = lY;
            view.rotation = landerBody.GetAngle() * (180/Math.PI);
        };

        for (let i=0; i<2; i++) {
            const fX = unscaled(feetBodies[i].GetPosition().x)
            const fY = unscaled(feetBodies[i].GetPosition().y)
            footViews[i].x = fX;
            footViews[i].y = fY;
            footViews[i].rotation = feetBodies[i].GetAngle() * (180/Math.PI);
            legViews[i].graphics.clear().ss(3, caps=1, joins=1).s(params.colors.legs).mt(lX,lY).lt(fX,fY);
        };
        stage.update()
    };

    // Report game play variables
    function report() {
        metrics = {
            'wind' : world.m_gravity.x.toFixed(2),
            'x, y' : [unscaled(landerBody.GetPosition().x).toFixed(0), unscaled(landerBody.GetPosition().y).toFixed(0)],
            'angle' : toDegrees(landerBody.GetAngle()).toFixed(0),
            'distance' : distToLandPoint.toFixed(1),
            'landed' : landed,
            'since landed' : sinceEnter.toFixed(1),
            'play time (s)': inSec(createjs.Ticker.getTime(true)).toFixed(1),
            'fuel' : fuel,
        }
        logGame(metrics);
    };

    // RequestAnimationFrame callback
    function tick() {
        currentTime = new Date().getTime();
            if (lastUpdateTime) {
                update(inSec(currentTime - lastUpdateTime))
                draw();
                if (params.hyper.logData) {report()};
            }
            lastUpdateTime = currentTime;
            requestAnimationFrame(tick, canvas);
        };

    // Check if lander is in land box
    function landerInBox(x, y, boxCenter) {
        return (Math.abs(boxCenter[0] - x) < 3*chunkWidth) && (Math.abs(boxCenter[1] - y) < params.lander.h*2)
    };

    // Sensor in box
    function sensorInBox(x, y, boxCenter) {
        return (Math.abs(boxCenter[0] - x) < 3*chunkWidth) && (Math.abs(boxCenter[1] - y) < 10)
    };

    // If the page is hidden, pause physics, else continue
    function reportVisibilityChange() {
        if (document[hidden]) {
            document.title = 'Paused';
            gamePaused = true;
            createjs.Ticker.paused = true;
            return true;
        }
      };

    // Pause or unpause game
    function pauseUnpause(gameIsPaused) {
        if (gameIsPaused) {
            createjs.Ticker.paused = true;
            stage.addChild(pauseBackground);
            stage.addChild(pauseMessage);
        } else {
            createjs.Ticker.paused = false;
            stage.removeChild(pauseBackground);
            stage.removeChild(pauseMessage)
        };
    };

    // Handle begin collision events
    function onBeginContact (contact) {
        let kindA = contact.GetFixtureA().GetBody().GetUserData().kind;
        let kindB = contact.GetFixtureB().GetBody().GetUserData().kind;
        // console.log(`Collision: ${kindA}::${kindB}`);
        if (kindA=='lander' || kindB=='lander') {let gameOver = true; endTrial()};
    };
};

function addChunk(xPos, yPos, chunkWidth, chunkHeight, left, right, world, stg) {
    vertices = [
        new Box2D.Common.Math.b2Vec2(-scaled(chunkWidth/2), -scaled(chunkHeight/2+left)),     // top left
        new Box2D.Common.Math.b2Vec2( scaled(chunkWidth/2), -scaled(chunkHeight/2+right)),    // top right
        new Box2D.Common.Math.b2Vec2( scaled(chunkWidth/2),  scaled(chunkHeight/2)),          // bottom right
        new Box2D.Common.Math.b2Vec2(-scaled(chunkWidth/2),  scaled(chunkHeight/2))           // bottom left
    ];

    const bodyDef = new Box2D.Dynamics.b2BodyDef();
    bodyDef.type = Box2D.Dynamics.b2Body.b2_staticBody;
    bodyDef.position.x = scaled(xPos);
    bodyDef.position.y = scaled(yPos);
    fixtDef = new Box2D.Dynamics.b2FixtureDef();
    fixtDef.density = 1;
    fixtDef.friction = params.floor.friction;
    fixtDef.restitution = params.floor.restitution;
    fixtDef.shape = new Box2D.Collision.Shapes.b2PolygonShape();
    fixtDef.shape.SetAsArray(vertices, vertices.length);
    chunkBody = world.CreateBody(bodyDef);
    chunkBody.SetUserData({kind:'floor'})
    chunkBody.CreateFixture(fixtDef);
    return chunkBody;
};

function getLanderParts(xPos, yPos, density, friction, restitution, world) {
    let feet = {
        bodies : Array(),
        fixtures : Array(),
        joints : Array(),
        views : Array()
    };
    let legs = {views : Array()}
    const xTop = params.lander.hullVerts.top.x, yTop = params.lander.hullVerts.top.y;
    const xMid = params.lander.hullVerts.mid.x, yMid = params.lander.hullVerts.mid.y;
    const xBot = params.lander.hullVerts.bot.x, yBot = params.lander.hullVerts.bot.y;
    const domeRadius = params.lander.hullVerts.mid.x-2;
    const vertices = [
        new Box2D.Common.Math.b2Vec2( scaled(xTop), scaled(yTop)),  // right top
        new Box2D.Common.Math.b2Vec2( scaled(xMid), scaled(yMid)),           // right middle
        new Box2D.Common.Math.b2Vec2( scaled(xBot), scaled(yBot)),   // right bottom
        new Box2D.Common.Math.b2Vec2(-scaled(xBot), scaled(yBot)),   // left bottom
        new Box2D.Common.Math.b2Vec2(-scaled(xMid), scaled(yMid)),           // left middle
        new Box2D.Common.Math.b2Vec2(-scaled(xTop), scaled(yTop))   // left top
    ];

    const setProps = (fxDf, f, d, r) => {fxDf.friction=f; fxDf.density=d; fxDf.restitution=r};

    // Capsule and Dome fixture defs
    const hullFixtDef = new Box2D.Dynamics.b2FixtureDef();
    setProps(hullFixtDef, friction, density, restitution)
    hullFixtDef.shape = new Box2D.Collision.Shapes.b2PolygonShape();
    hullFixtDef.shape.SetAsArray(vertices, vertices.length);
    const domeFixtDef = new Box2D.Dynamics.b2FixtureDef();
    domeFixtDef.shape = new Box2D.Collision.Shapes.b2CircleShape(scaled(domeRadius));
    domeFixtDef.shape.m_p.Set(0, scaled(yTop));
    let hullFixt, domeFixt, sensFixt;

    // Lander body def
    const landerBodyDef = new Box2D.Dynamics.b2BodyDef();
    landerBodyDef.type = Box2D.Dynamics.b2Body.b2_dynamicBody;
    landerBodyDef.position.Set(scaled(xPos), scaled(yPos));
    landerBody = world.CreateBody(landerBodyDef);
    hullFixt = landerBody.CreateFixture(hullFixtDef);
    domeFixt = landerBody.CreateFixture(domeFixtDef);

    // Capsule and Dome view defs
    const hullView = new createjs.Shape();
    hullView.graphics.beginFill(params.colors.lander);
    hullView.graphics.moveTo( xTop, yTop);    // right top
    hullView.graphics.lineTo( xMid, yMid);    // right middle
    hullView.graphics.lineTo( xBot, yBot);    // right bottom
    hullView.graphics.lineTo(-xBot, yBot);    // left bottom
    hullView.graphics.lineTo(-xMid, yMid);    // left middle
    hullView.graphics.lineTo(-xTop, yTop);    // left top
    const domeView = new createjs.Shape();
    domeView.graphics.beginFill(params.colors.dome).drawCircle(0, 0, domeRadius);
    domeView.regY = -yTop;

    // Feet body, fixture, and joint defs
    for (let i of [-1, 1]) {
        let footBodyDef = new Box2D.Dynamics.b2BodyDef();
        footBodyDef.type = Box2D.Dynamics.b2Body.b2_dynamicBody;
        footBodyDef.position.Set(scaled(xPos + i*params.lander.footOff.x), scaled(yPos + params.lander.footOff.y));
        let footFixtDef = new Box2D.Dynamics.b2FixtureDef();
        setProps(footFixtDef, friction, params.lander.footDensity, 0)
        footFixtDef.shape = new Box2D.Collision.Shapes.b2PolygonShape();
        footFixtDef.shape.SetAsBox(scaled(params.lander.footW), scaled(params.lander.footH));
        footBody = world.CreateBody(footBodyDef);
        footBody.SetUserData({kind : i<0 ? 'foot1' : 'foot2'});
        feet.bodies.push(footBody);
        feet.fixtures.push(footBody.CreateFixture(footFixtDef));
        for (let pivLander of [[xMid, yMid], [xBot, yBot], [xTop, yTop]]) {
            for (let pivFootX of [params.lander.footW/2, -params.lander.footW/2]) {
                let joint = addLanderJoint(
                    landerBody = landerBody,
                    footBody = footBody,
                    pivLander = [pivLander[0], pivLander[1]-params.lander.footH/2],
                    pivFoot = [pivFootX, -params.lander.footH/2],
                    offset = params.lander.footOff,
                    side = i
                );
                joint = world.CreateJoint(joint);
                feet.joints.push(joint);
            };
        };
        const footView = new createjs.Shape();
        footView.graphics.beginFill(params.colors.feet).drawRect(
            -params.lander.footW/2-5, -2, params.lander.footW+10, params.lander.footH+4);
        feet.views.push(footView);
        legs.views.push(new createjs.Shape());
    };

    // Add a ghost joint to connect the feet
    const feetJointDef = new Box2D.Dynamics.Joints.b2DistanceJointDef();
    feetJointDef.bodyA = feet.bodies[0];
    feetJointDef.bodyB = feet.bodies[1];
    feetJointDef.length = scaled(params.lander.footOff.x*2);
    feetJoint = world.CreateJoint(feetJointDef);

    // Add a ghost body as sensor
    const sensorFixtDef = new Box2D.Dynamics.b2FixtureDef();
    sensorFixtDef.shape = new Box2D.Collision.Shapes.b2CircleShape(scaled(5));
    sensorFixtDef.isSensor = true;
    const sensorBodyDef = new Box2D.Dynamics.b2BodyDef();
    sensorBodyDef.type = Box2D.Dynamics.b2Body.b2_dynamicBody;
    sensorBodyDef.position.Set(scaled(xPos), scaled(yPos+params.lander.footOff.y+10));
    sensorBody = world.CreateBody(sensorBodyDef);
    sensorBody.SetUserData({kind: 'sensor'})
    sensorFixt = sensorBody.CreateFixture(sensorFixtDef);
    const l = getEuclidDistance([params.lander.hullVerts.mid.x, 0], [0, params.lander.footOff.y+10])
    for (let i of [-1, 1]) {
        sensorJointDef = new Box2D.Dynamics.Joints.b2DistanceJointDef();
        sensorJointDef.bodyA = sensorBody;
        sensorJointDef.bodyB = landerBody;
        sensorJointDef.localAnchorB.Set(scaled(i*params.lander.hullVerts.mid.x), 0)
        sensorJointDef.length = scaled(l);
        world.CreateJoint(sensorJointDef);
    };

    return {
        bodies : {
            lander : landerBody,
            feet : feet.bodies,
            sensor : sensorBody,
        },
        views : {
            feet : feet.views,
            legs : legs.views,
            lander : [domeView, hullView]
        }
    }
};

function addLanderJoint(landerBody, footBody, pivLander, pivFoot, offset, side) {
    const footJointDef = new Box2D.Dynamics.Joints.b2DistanceJointDef();
    const v = [side*pivLander[0], pivLander[1]]; // pivot point on Lander
    const u = [side*pivFoot[0], pivFoot[1]]; // pivot point on Foot (in foot coords)
    const u_ = [side*(pivFoot[0]+offset.x), pivFoot[1]+offset.y] // pivot point on Foot (in lander coords)
    footJointDef.bodyA = landerBody;
    footJointDef.bodyB = footBody;
    footJointDef.localAnchorA.Set(scaled(v[0]), scaled(v[1]))
    footJointDef.localAnchorB.Set(scaled(u[0]), scaled(u[1]))
    footJointDef.length = scaled(getEuclidDistance(v, u_));
    footJointDef.frequencyHz = params.lander.springFreq;
    footJointDef.dampingRatio = params.lander.springDamp;
    footJointDef.collideConnected = true;
    return footJointDef
};
