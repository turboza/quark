module Quark
require "quark"
def self.constructors; Constructors; end
module Constructors
require_relative 'test1' # 0 () ()
require_relative 'test2' # 0 () ()
require_relative 'test3' # 0 () ()
require_relative 'constructors' # 0 () ()

def self.main()
    
    ::Quark.test1.go()
    ::Quark.test2.go()
    ::Quark.test3.go()


    nil
end

if __FILE__ == $0
    ::Quark.constructors.main()
end

end # module Constructors
end # module Quark
