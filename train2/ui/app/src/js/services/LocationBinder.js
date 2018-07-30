export default function LocationBinder($location) {
    'ngInject';
    return {
        bind: function(scope, scopeProperty, locationProperty, parser, formatter) {
            //console.log(`In bind of ${scopeProperty} url=${angular.toJson($location.search())}`);
            scope[scopeProperty] = $location.search()[locationProperty] || null;

            scope.$watch(scopeProperty, function(value) {
                //console.log("watch on property:", locationProperty, value);

                if (formatter)
                    value = formatter(value);

                $location.search(locationProperty, value);
            });

            scope.$watch(function() { return $location.search()[locationProperty] || null; }, function(value) {
                //console.log("watch on url:", locationProperty, value);
                if (parser)
                    value = parser(value);

                scope[scopeProperty] = value;
            });
        }
    };
};

