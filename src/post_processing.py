import moderngl
import numpy as np
import pygame

class PostProcessor:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # Initialize ModernGL context (requires existing OpenGL context from Pygame)
        try:
            self.ctx = moderngl.create_context()
        except Exception as e:
            print(f"[Post-Process] Error creating ModernGL context: {e}")
            self.ctx = None
            return

        # Vertex Shader: Simple fullscreen quad
        self.v_shader = """
        #version 330
        in vec2 in_vert;
        in vec2 in_texcoord;
        out vec2 v_texcoord;
        void main() {
            gl_Position = vec4(in_vert, 0.0, 1.0);
            v_texcoord = in_texcoord;
        }
        """

        # Fragment Shader: Bloom + Vignette + Chromatic Aberration + Ambient Tint
        self.f_shader = """
        #version 330
        uniform sampler2D Texture;
        uniform float time;
        uniform vec3 u_ambient_tint;
        in vec2 v_texcoord;
        out vec4 f_color;

        void main() {
            vec2 uv = v_texcoord;
            
            // Base color from texture
            vec3 color = texture(Texture, uv).rgb;

            // 3. Simple Vignette (Subtle)
            float dist = distance(uv, vec2(0.5));
            float vignette = 1.0 - smoothstep(0.6, 1.1, dist);
            color *= vignette;

            // 4. Ambient Tint (Day/Night Cycle)
            color *= u_ambient_tint;

            f_color = vec4(color, 1.0);
        }
        """

        self.program = self.ctx.program(vertex_shader=self.v_shader, fragment_shader=self.f_shader)
        
        # Screen quad vertices (triangle strip)
        # x, y, u, v
        # Final UV mapping: Pygame Row 0 (Top) -> GL Textue Row 0 (Bottom)
        # Vertex TL (-1, 1) samples GL Bottom-Left (0, 0)
        # Vertex BL (-1, -1) samples GL Top-Left (0, 1)
        vertices = np.array([
            -1.0,  1.0, 0.0, 0.0,  # Top Left
            -1.0, -1.0, 0.0, 1.0,  # Bottom Left
             1.0,  1.0, 1.0, 0.0,  # Top Right
             1.0, -1.0, 1.0, 1.0,  # Bottom Right
        ], dtype='f4')
        
        self.vbo = self.ctx.buffer(vertices)
        self.vao = self.ctx.simple_vertex_array(self.program, self.vbo, 'in_vert', 'in_texcoord')
        
        # Texture to hold the Pygame surface data
        self.screen_texture = self.ctx.texture((width, height), 4)
        self.screen_texture.repeat_x = False
        self.screen_texture.repeat_y = False
        
        print("[Post-Process] Shaders compiled and pipeline ready.")

    def render(self, surface, rgb_tint=(1.0, 1.0, 1.0)):
        if not self.ctx: return
        
        # Convert Pygame surface to raw bytes and update ModernGL texture
        buffer = surface.get_view('1')
        self.screen_texture.write(buffer)
        
        # Update uniforms
        if 'u_ambient_tint' in self.program:
            self.program['u_ambient_tint'].value = rgb_tint
        
        # Bind texture and render quad
        self.ctx.clear(0, 0, 0)
        self.screen_texture.use()
        self.vao.render(moderngl.TRIANGLE_STRIP)
