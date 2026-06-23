#!/usr/bin/env python3
"""
MCP Server para Análisis de Mercado de Apuestas
Proporciona herramientas para conversión de cuotas y comparación de probabilidades
"""

from mcp.server import Server
from mcp.types import Tool, TextContent
import json

# Crear servidor MCP
app = Server("wc-market-mcp")

@app.tool(
    name="convertir_cuota_a_probabilidad",
    description="Convierte cuota decimal a probabilidad implícita"
)
async def convertir_cuota_a_probabilidad(cuota: float) -> list[TextContent]:
    """
    Convierte cuota decimal a probabilidad usando la fórmula: prob = 1 / cuota
    """
    try:
        if cuota <= 0:
            return [TextContent(
                type="text",
                text=json.dumps({"error": "La cuota debe ser mayor a 0"}, indent=2)
            )]
        
        probabilidad = 1.0 / cuota
        probabilidad_porcentaje = probabilidad * 100
        
        result = {
            "cuota_decimal": cuota,
            "probabilidad": probabilidad,
            "probabilidad_porcentaje": probabilidad_porcentaje,
            "formula": "prob = 1 / cuota"
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, indent=2)
        )]

@app.tool(
    name="comparar_probabilidades",
    description="Compara probabilidad del modelo con cuota del mercado y calcula brecha de confianza"
)
async def comparar_probabilidades(prob_ia: float, cuota_mercado: float) -> list[TextContent]:
    """
    Compara la probabilidad predicha por la IA con la cuota del mercado.
    Devuelve una brecha de confianza que indica si hay valor en la apuesta.
    """
    try:
        # Convertir cuota a probabilidad del mercado
        prob_mercado = 1.0 / cuota_mercado if cuota_mercado > 0 else 0
        
        # Calcular brecha de confianza
        brecha = prob_ia - prob_mercado
        brecha_porcentaje = brecha * 100
        
        # Determinar nivel de confianza
        if brecha > 0.15:
            nivel_confianza = "ALTO - Valor positivo significativo"
            recomendacion = "Considerar apuesta (brecha > 15%)"
        elif brecha > 0.05:
            nivel_confianza = "MEDIO - Valor positivo moderado"
            recomendacion = "Evaluar con cautela (brecha 5-15%)"
        elif brecha > -0.05:
            nivel_confianza = "NEUTRO - Sin valor claro"
            recomendacion = "No hay valor significativo"
        elif brecha > -0.15:
            nivel_confianza = "MEDIO - Valor negativo moderado"
            recomendacion = "Evitar apuesta (brecha -5% a -15%)"
        else:
            nivel_confianza = "BAJO - Valor negativo significativo"
            recomendacion = "No apostar (brecha < -15%)"
        
        result = {
            "prob_ia": prob_ia,
            "prob_ia_porcentaje": prob_ia * 100,
            "cuota_mercado": cuota_mercado,
            "prob_mercado": prob_mercado,
            "prob_mercado_porcentaje": prob_mercado * 100,
            "brecha": brecha,
            "brecha_porcentaje": brecha_porcentaje,
            "nivel_confianza": nivel_confianza,
            "recomendacion": recomendacion
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, indent=2)
        )]

@app.tool(
    name="analizar_valor_apuesta",
    description="Analiza si una apuesta tiene valor basado en probabilidad y cuota"
)
async def analizar_valor_apuesta(prob_ia: float, cuota_mercado: float, stake: float = 100.0) -> list[TextContent]:
    """
    Análisis completo de valor de apuesta incluyendo ROI esperado
    """
    try:
        prob_mercado = 1.0 / cuota_mercado if cuota_mercado > 0 else 0
        brecha = prob_ia - prob_mercado
        
        # Calcular ROI esperado
        roi_esperado = (prob_ia * cuota_mercado - 1) * 100
        
        # Calcular valor esperado
        valor_esperado = (prob_ia * (cuota_mercado - 1) - (1 - prob_ia)) * stake
        
        # Determinar si tiene valor
        tiene_valor = brecha > 0.05
        
        result = {
            "prob_ia": prob_ia,
            "cuota_mercado": cuota_mercado,
            "prob_mercado": prob_mercado,
            "brecha": brecha,
            "brecha_porcentaje": brecha * 100,
            "roi_esperado": roi_esperado,
            "valor_esperado": valor_esperado,
            "stake": stake,
            "tiene_valor": tiene_valor,
            "analisis": "Valor positivo" if tiene_valor else "Sin valor claro"
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, indent=2)
        )]

async def main():
    """Inicia el servidor MCP"""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
