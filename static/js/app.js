(function () {
    "use strict";
    var fixOriginX = 0;
    var fixOriginY = 0;

    var ImageListView = {
        el: document.getElementById('imagesListView'),

        createImageListElement: function (image) {
            var imageListElement = document.createElement("button");
            imageListElement.classList.add('list-group-item');
            imageListElement.innerText = image.name;
            imageListElement.addEventListener('click', function onClick(event) {
                event.preventDefault();
                MainController.updateCurrentImage(image);
            });
            return imageListElement;
        },

        render: function (images) {
            for (var i = 0; i < images.length; i++) {
                var currentImagePath = images[i];
                this.el.appendChild(this.createImageListElement(currentImagePath));
            }
        }
    };


    var CurrentImageView = {
        el: document.getElementById('currentImageView'),

        image: null,

        init: function () {
            var context = this.el.getContext('2d');
            this.image = new Image();
            this.image.onload = function () {
                window.requestAnimationFrame(function () {
                    context.drawImage(this.image, 0, 0, this.image.width, this.image.height);
                }.bind(CurrentImageView));
            };

            this.el.addEventListener('click', function (event) {
                event.preventDefault();

                var boundingRect = this.el.getBoundingClientRect();
                var position = {
                    x: event.x,
                    y: event.y
                };

                CoordinateTransformService.getWorldCoordinates(getPositionRelativeTo(position, boundingRect));
            }.bind(this));
        },

        render: function (image_url) {
            this.image.src = image_url;
        }
    };

    var CursorPositionView = {
        el: document.getElementById('cursorPositionView'),

        render: function (position) {
            requestAnimationFrame(function () {
                this.el.innerText = "(" + position.x.toString() + ", " + position.y.toString() + ")";
            }.bind(this));
        }
    };

    var CoordinateTransformView = {
        el: document.getElementById('coordinateTransformView'),

        render: function (image, world) {
            requestAnimationFrame(function () {
                this.el.innerText = "(" + image.x.toString() + ", " + image.y.toString() + ")" + " --> " +
                    "(" + world.x.toString() + ", " + world.y.toString() + ", " + world.z.toString() + ")";
            }.bind(this));
        }
    };

    var CalibrationButton = {
        el: document.getElementById('showCalibrationPoints'),

        init: function () {
            this.el.addEventListener('click', function (event) {
                event.preventDefault();

                var currentImage = MainController.getCurrentImage();
                CurrentImageView.render(currentImage.chessboard_url);
            });
        }
    };

    var CoordinateTransformService = {
        z: 0.0,

        getWorldCoordinates: function (coordinates) {
            coordinates.z = this.z;
            var coordinateTransformRequest = new XMLHttpRequest();
            coordinateTransformRequest.onload = function (event) {
                var data = JSON.parse(event.target.response);

                var worldCoordinates = {
                    x: data.world_coordinates[0].toFixed(3),
                    y: data.world_coordinates[1].toFixed(3),
                    z: data.world_coordinates[2].toFixed(3)
                };

                CoordinateTransformView.render(coordinates, worldCoordinates);
            };
            coordinateTransformRequest.open('POST', 'http://localhost:5000/world_coordinates');
            coordinateTransformRequest.setRequestHeader('Content-Type', 'application/json, charset=utf-8;');
            coordinateTransformRequest.send(JSON.stringify(coordinates));
        },

        setZ: function (zElement) {
            switch (zElement) {
                case 'table':
                    this.z = 0.0;
                    break;
                case 'robot':
                    this.z = 20.0 / 4.7;
                    break;
                case 'obstacle':
                    this.z = 41.0 / 4.7;
                    break;
            }
        }
    };

    var FixOriginButton = {
        el: document.getElementById('fixOrigin'),

        init: function () {
            this.el.addEventListener('click', function (event) {
                event.preventDefault();
                var fixOriginXY = document.getElementById("originXY").value.split(",");
                if(!isNaN(fixOriginXY[0]) && !isNaN(fixOriginXY[1])){
                     fixOriginX = fixOriginXY[0];
                     fixOriginY = fixOriginXY[1];
                }
            });
        }
    };

    var ImageDistortionButton = {
        el: document.getElementById('showUndistorted'),

        distorted: false,

        init: function () {
            this.el.addEventListener('click', function (event) {
                event.preventDefault();

                if (this.distorted) {
                    this.distorted = false;
                    this.el.innerHTML = "show original";
                    MainController.showUndistortedImage();
                } else {
                    this.distorted = true;
                    this.el.innerHTML = "show undistorted";
                    MainController.showOriginalImage();
                }
            }.bind(this));
        },

        reset: function () {
            this.distorted = false;
            this.el.innerHTML = "show original";
        }
    };

    var MainController = {
        currentImage: null,

        init: function (images) {
            ImageListView.render(images.calibration.images);
            this.updateCurrentImage(images.calibration.images[3]);
            this.showUndistortedImage();
        },

        showUndistortedImage: function () {
            CurrentImageView.render(this.currentImage.undistorted_url);
        },

        showOriginalImage: function () {
            CurrentImageView.render(this.currentImage.url);
        },

        updateCurrentImage: function (image) {
            this.currentImage = image;
            ImageDistortionButton.reset();
            CurrentImageView.render(this.currentImage.undistorted_url);
        },

        getCurrentImage: function () {
            return this.currentImage;
        }
    };

    var ImageService = {
        getImagesInfos: function (callback) {
            var imagesInfosRequest = new XMLHttpRequest();
            imagesInfosRequest.onload = function (event) {
                var data = JSON.parse(event.target.response);
                callback(data);
            };
            imagesInfosRequest.open("GET", 'http://localhost:5000/images-infos');
            imagesInfosRequest.send();
        }
    };

    function getPositionRelativeTo(cursorPosition, boundingRect) {
        return {
            x: cursorPosition.x - boundingRect.left - fixOriginX,
            y: cursorPosition.y - boundingRect.top - fixOriginY
        };
    }

    window.addEventListener('mousemove', function (event) {
        if (event.target === CurrentImageView.el) {
            var boundingRect = event.target.getBoundingClientRect();
            var position = {
                x: event.x,
                y: event.y
            };

            CursorPositionView.render(getPositionRelativeTo(position, boundingRect));
        }
    });

    var selectZ = document.getElementById('selectZ');
    for (var i = 0; i < selectZ.length; i++) {
        selectZ[i].onclick = function () {
            CoordinateTransformService.setZ(this.value);
        };
    }

    CurrentImageView.init();
    CalibrationButton.init();
    ImageDistortionButton.init();
    FixOriginButton.init();

    ImageService.getImagesInfos(MainController.init.bind(MainController));
}());
