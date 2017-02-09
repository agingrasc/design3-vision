var gulp = require('gulp');
var browserSync = require('browser-sync');

gulp.task('styles', function () {
    gulp.src('node_modules/bootstrap/dist/css/bootstrap.css')
        .pipe(gulp.dest('./app/css'));
});

gulp.task('default', ['styles'], function () {
    gulp.watch('./app/**/*.css', browserSync.reload);
    gulp.watch('./app/index.html', browserSync.reload);
    gulp.watch('./app/js/**/*.js', browserSync.reload);

    browserSync.init({
        server: './app/'
    });

    browserSync.stream();
});
