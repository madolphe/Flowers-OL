const params = {
    debug: false,
    gravity : 0,
    scale : 5,
    lander : {
        w : 120,
        h : 90,
        damping : 10,
        density : .01,
        thrust : 30,
        turning : 10,
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
        pauseText: '#f07a56',
        canvasBorder: '#252938',

    },
    hyper : {
        updatePeriod : 1/80,                     // simulation step size (seconds)
        positionIterations : 3,
        velocityIterations : 8
    }
};
const scaled = (x) => {return x/params.scale};
const unscaled = (x) => {return x*params.scale};
const getEuclidDistance = (u, w) => {return Math.sqrt((u[0]-w[0])**2+(u[1]-w[1])**2)};
const inSec = (ms) => {return ms/1000};

function runTutorial() {
    const canvas = document.getElementById('id-tutorial-canvas');
    const context = canvas.getContext('2d');
    const stage = new createjs.Stage(canvas);
    let world;
    let landerBody;
    let hullView;
    let lastUpdateTime;
    let accumulator = 0;
    canvas.style.backgroundColor = params.colors.sky;

    init();

    // Run initializers
    function init() {
        world = new Box2D.Dynamics.b2World(
            new Box2D.Common.Math.b2Vec2(0, params.gravity), true);
        initKeyboard();
        initLander();
        if (params.debug){initBox2DDebug()}
        trialStartTime = new Date().getTime();
        createjs.Ticker.addEventListener('tick', draw);
        createjs.Ticker.useRAF = true;
        trialStart = true;
        tick();
    };

    //Initializes keyboard events
    function initKeyboard() {
        canvas.addEventListener('keydown', function (event) {
            if (32 == event.keyCode) {
                landerBody.GetUserData().thrusting = true;
            } else if (70 == event.keyCode) {
                landerBody.GetUserData().turningLeft = true;
            } else if (74 == event.keyCode) {
                landerBody.GetUserData().turningRight = true;
            } else if (event.keyCode == 32 && event.target == document.body) {
              event.preventDefault();
            }
        });

        canvas.addEventListener('keyup', function (event) {
            if (32 == event.keyCode) {
                landerBody.GetUserData().thrusting = false;
            } else if (70 == event.keyCode) {
                landerBody.GetUserData().turningLeft = false;
            } else if (74 == event.keyCode) {
                landerBody.GetUserData().turningRight = false;
            }
        });
    };

    // Initialize the lander
    function initLander() {
        let landerData = {
            'width' : params.lander.w,
            'height' : params.lander.h,
            'thrusting' : false,
            'turningLeft' : false,
            'turningRight' : false,
            'thrust' : params.lander.thrust,
            'turning' : params.lander.turning,
        };

        const xPos = canvas.width/2
        const yPos = canvas.height/2;

        const hullFixtDef = new Box2D.Dynamics.b2FixtureDef();
        hullFixtDef.friction=1;
        hullFixtDef.density=params.lander.density;
        hullFixtDef.restitution=1;
        hullFixtDef.shape = new Box2D.Collision.Shapes.b2PolygonShape();
        hullFixtDef.shape.SetAsBox(scaled(params.lander.w/2), scaled(params.lander.h/2));

        // Lander body def
        const landerBodyDef = new Box2D.Dynamics.b2BodyDef();
        landerBodyDef.type = Box2D.Dynamics.b2Body.b2_dynamicBody;
        landerBodyDef.position.Set(scaled(xPos), scaled(yPos));
        landerBody = world.CreateBody(landerBodyDef);
        landerBody.SetUserData(landerData);
        landerBody.SetLinearDamping(params.lander.damping)
        landerBody.SetAngularDamping(params.lander.damping)
        let hullFixt = landerBody.CreateFixture(hullFixtDef);

        hullView = new createjs.Bitmap("../static/images/lunar_lander/lander.png");
        hullView.scaleY = 9/12
        stage.addChild(hullView)
    };

    // Simulate physics for time period `dt`
    function simulate(dt) {
        let impulse;
        let steeringPoint;
        let shipData = landerBody.GetUserData();
        let landerXpx = unscaled(landerBody.GetPosition().x)
        let landerYpx = unscaled(landerBody.GetPosition().y)

        if (shipData.thrusting) {
            impulse = new Box2D.Common.Math.b2Vec2(Math.sin(landerBody.GetAngle()) * shipData.thrust,
                -(Math.cos(landerBody.GetAngle()) * shipData.thrust));
            landerBody.ApplyImpulse(impulse, landerBody.GetWorldCenter());
        }

        if (shipData.turningLeft || shipData.turningRight) {
            steeringPoint1 = landerBody.GetWorldCenter().Copy();
            steeringPoint1.y -= scaled(shipData.height/2);
            steeringPoint2 = landerBody.GetWorldCenter().Copy();
            steeringPoint2.y += scaled(shipData.height/2);
        }
        if (shipData.turningLeft) {
            impulse = new Box2D.Common.Math.b2Vec2(-shipData.turning, 0);
            landerBody.ApplyImpulse(impulse, steeringPoint1);
            impulse = new Box2D.Common.Math.b2Vec2(shipData.turning, 0);
            landerBody.ApplyImpulse(impulse, steeringPoint2);
        }
        if (shipData.turningRight) {
            impulse = new Box2D.Common.Math.b2Vec2(shipData.turning, 0);
            landerBody.ApplyImpulse(impulse, steeringPoint1);
            impulse = new Box2D.Common.Math.b2Vec2(-shipData.turning, 0);
            landerBody.ApplyImpulse(impulse, steeringPoint2);
        }

        margin = params.lander.w/3
        let wrapX, wrapY
        if (landerXpx > canvas.width+margin) {
            wrapX = new Box2D.Common.Math.b2Vec2(scaled(-margin), scaled(landerYpx))
            landerBody.SetPosition(wrapX, landerBody.GetAngle());}
        if (landerXpx < -margin) {
            wrapX = new Box2D.Common.Math.b2Vec2(scaled(canvas.width+margin), scaled(landerYpx))
            landerBody.SetPosition(wrapX, landerBody.GetAngle());}

        if (landerYpx > canvas.height+margin) {
            wrapY = new Box2D.Common.Math.b2Vec2(scaled(landerXpx), -scaled(margin))
            landerBody.SetPosition(wrapY, landerBody.GetAngle());}
        if (landerYpx < -margin) {
            wrapY = new Box2D.Common.Math.b2Vec2(scaled(landerXpx), scaled(canvas.height+margin))
            landerBody.SetPosition(wrapY, landerBody.GetAngle());}


        world.Step(dt, params.hyper.velocityIterations, params.hyper.positionIterations);
    };

    // Time-update function to handle variable frame rate
    function update(dt) {
        accumulator += (dt)
        while (accumulator > params.hyper.updatePeriod) {
            simulate(params.hyper.updatePeriod);
            accumulator -= params.hyper.updatePeriod;
        }
    }

    //Draw world
    function draw() {
        if (params.debug) {world.DrawDebugData();}
        const lX = unscaled(landerBody.GetPosition().x);
        const lY = unscaled(landerBody.GetPosition().y);
        hullView.regX = params.lander.w/2;
        hullView.regY = params.lander.h/2 + (3/12)*params.lander.h;
        hullView.x = lX
        hullView.y = lY
        // console.log(hullView.regX, hullView.regY)
        hullView.rotation = landerBody.GetAngle() * (180/Math.PI);
        stage.update()
        // console.log(`${lX}, ${lY}`)
    };

    // RequestAnimationFrame callback
    function tick() {
        currentTime = new Date().getTime();
        if (lastUpdateTime) {
            update(inSec(currentTime - lastUpdateTime))
            draw();
        }
        lastUpdateTime = currentTime;
        requestAnimationFrame(tick, canvas);
    };

    //Initialize Box2D debug
    function initBox2DDebug() {
        let debugDraw = new Box2D.Dynamics.b2DebugDraw();
        debugDraw.SetSprite(debugContext);
        debugDraw.SetDrawScale(params.scale);
        debugDraw.SetFillAlpha(.1);
        debugDraw.SetLineThickness(1);
        debugDraw.SetFlags(Box2D.Dynamics.b2DebugDraw.e_shapeBit | Box2D.Dynamics.b2DebugDraw.e_jointBit);
        world.SetDebugDraw(debugDraw);
    };

};


runTutorial();