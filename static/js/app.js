(function () {
    "use strict";


    var CalibrationImagesListView = {
        el: document.getElementById('calibrationImagesListView'),
        imageCount: document.getElementById('imageCount'),

        render: function (images) {
            this.imageCount.innerText = images.length.toString();

            for (var i = 0; i < images.length; i++) {
                var currentImagePath = images[i];
                var listElement = createImageListElement(currentImagePath);
                this.el.appendChild(listElement);
            }
        }
    };

    var CurrentImageView = {
        el: document.getElementById('currentImageView'),

        init: function () {
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

        render: function (image) {
            window.requestAnimationFrame(function () {
                this.el.src = image.url;
            }.bind(this));
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
                CurrentImageView.render({url: currentImage.chessboard_url});
            });
        }
    };

    var CoordinateTransformService = {
        getWorldCoordinates: function (coordinates) {
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
        }
    };

    var ImageDistortionButton = {
        el: document.getElementById('showUndistorted'),

        distorted: true,

        init: function () {
            this.el.addEventListener('click', function (event) {
                event.preventDefault();

                if (this.distorted) {
                    this.distorted = false;
                    this.el.innerHTML = "normal";
                    MainController.showDistortedImage();
                } else {
                    this.distorted = true;
                    this.el.innerHTML = "undistort";
                    MainController.showNormalImage();
                }
            }.bind(this));
        },

        reset: function () {
            this.distorted = true;
            this.el.innerHTML = "undistort";
        }
    };

    var MainController = {
        currentImage: null,

        init: function (images) {
            CalibrationImagesListView.render(images.calibration.images);

            this.updateCurrentImage(images.calibration.images[0]);

            CurrentImageView.render(this.currentImage);
        },

        showDistortedImage: function () {
            CurrentImageView.render({url: this.currentImage.undistorted_url});
        },

        showNormalImage: function () {
            CurrentImageView.render({url: this.currentImage.url});
        },

        getCurrentImage: function () {
            return this.currentImage;
        },

        updateCurrentImage: function (image) {
            this.currentImage = image;

            ImageDistortionButton.reset();

            CurrentImageView.render(image);
        }
    };

    var ImageService = {
        getImagesInfos: function (callback) {
            var imagesInfosRequest = new XMLHttpRequest();
            imagesInfosRequest.onload = function (event) {
                callback(JSON.parse(event.target.response));
            };
            imagesInfosRequest.open("GET", 'http://localhost:5000/images-infos');
            imagesInfosRequest.send();
        }
    };

    function getPositionRelativeTo(cursorPosition, boundingRect) {
        return {
            x: cursorPosition.x - boundingRect.left,
            y: cursorPosition.y - boundingRect.top
        };
    }

    function createImageListElement(image) {
        var imageListElement = document.createElement("button");
        imageListElement.classList.add('list-group-item');
        imageListElement.innerText = image.name;
        imageListElement.addEventListener('click', function onClick(event) {
            event.preventDefault();

            MainController.updateCurrentImage(image);
        });
        return imageListElement;
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

    CurrentImageView.init();
    CalibrationButton.init();
    ImageDistortionButton.init();

    ImageService.getImagesInfos(MainController.init.bind(MainController));
}());
