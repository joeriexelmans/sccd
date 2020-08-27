<?xml version="1.0"?>
<xsl:stylesheet
    version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:scxml="http://www.w3.org/2005/07/scxml"
    xmlns:conf="http://www.w3.org/2005/scxml-conformance"
    xmlns="msdl.uantwerpen.be/sccd">
  <xsl:output method="xml" indent="yes"/>

  <xsl:template match="/">
    <diagram>
      <description>
        <xsl:value-of select="/comment()"/>
      </description>
      <class name="Class1" default="true">
        <xsl:apply-templates select="scxml:scxml"/>
      </class>
    </diagram>
  </xsl:template>

  <xsl:template match="/scxml:scxml">
    <scxml initial="{@initial}">
      <xsl:for-each select="scxml:state">
        <state id="{@id}">
        </state>
      </xsl:for-each>
      <xsl:for-each select="scxml:onentry">
        <onentry>
        </onentry>
      </xsl:for-each>
    </scxml>
  </xsl:template>

  <xsl:template match="scxml:state|scxml:scxml">
  </xsl:template>

<!--   <xsl:template match="onentry|onexit">

  </xsl:template>
 --></xsl:stylesheet>