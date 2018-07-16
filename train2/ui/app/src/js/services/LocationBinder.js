export default function LocationBinder($location) {
    'ngInject';
    return {
        bind: function(scope, scopeProperty, locationProperty, parser, formatter) {
            scope[scopeProperty] = $location.search()[locationProperty] || null;

            scope.$watch(scopeProperty, function(value) {
                if (formatter)
                    value = formatter(value);

                $location.search(locationProperty, value);
            });

            scope.$watch(function() { return $location.search()[locationProperty] || null; }, function(value) {
                if (parser)
                    value = parser(value);

                scope[scopeProperty] = value;
            });
        }
    };
};

