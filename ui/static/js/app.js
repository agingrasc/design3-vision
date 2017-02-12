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

                console.log(getPositionRelativeTo(position, boundingRect));
            }.bind(this));
        },

        render: function (image) {
            window.requestAnimationFrame(function () {
                this.el.src = image.src;
            }.bind(this));
        }
    };

    var CursorPositionView = {
        el: document.getElementById('cursorPositionView'),

        render: function (position) {
            this.el.innerText = "(" + position.x.toString() + ", " + position.y.toString() + ")";
        }
    };

    var MainController = {
        currentImage: null,

        init: function (images) {
            CalibrationImagesListView.render(images.calibration.images);

            this.currentImage = images.calibration.images[0];

            CurrentImageView.render(this.currentImage);
        },

        getCurrentImage: function () {
            return this.currentImage;
        },

        updateCurrentImage: function(image) {
            this.currentImage = image;

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

    var showCalibrationPointsButton = document.getElementById('showCalibrationPoints');

    showCalibrationPointsButton.addEventListener('click', function (event) {
        event.preventDefault();

        var currentImage = MainController.getCurrentImage();

        CurrentImageView.render({ src: currentImage.calibration_points })
    });

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

    ImageService.getImagesInfos(MainController.init.bind(MainController));
}());
